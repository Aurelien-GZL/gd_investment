import plotly.graph_objs as go
import requests
import uuid
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import status
from authentication.models import ApiKey
from authentication.views import ApiKeyAuthentication
from stocks.models import DailyTrade, DailyTradeLast, TradeVar, DailyTrade1Year, Company, IncomeStatement, StockAnalysis1Year
from stocks.forms import StocksEvolutionForm, StocksSelectionForm, ApiDailyForm
from stocks.serializers import DailyTradeSerializer


##########
# Constant
##########

bs_primary_rgb = '13, 110, 253'
bs_secondary_rgb = '108, 117, 125'

##########
# Generic functions
##########


def cache_data(context, original_data):
    """Cache data for a given context"""

    # Create a unique cache key for all TradeVar data
    cache_key = f'{context}_cached'

    # Try to get the data from the cache
    cached_data = cache.get(cache_key)

    # If the data is not in the cache or has expired, retrieve it from the database and store it in the cache
    if cached_data is None:
        # Store the original data in the cache with the unique cache key with an expiration time of 1 hour
        cache.set(cache_key, original_data, timeout=3600)

        # Set the cached_data to the original data
        cached_data = original_data

    return cached_data


def get_top_data(name: str, period: str, limit: int, order: str = ''):
    """Get top data for a specific time period"""
    data_db = TradeVar.objects \
        .values('symbol', 'close_value', var=F(period), var_perc=F(f'{period}_perc')) \
        .filter(var_perc__isnull=False) \
        .order_by(f'{order}var_perc') \
        .all()[:limit]
    return cache_data(f'{name}_{period}_db', data_db)


##########
# view function
##########


# Home page view
# ------------------------------
def home(request):
    """Return home page
    """
    # Return success signup message if any
    success_messages = messages.get_messages(request)
    signup_success = request.session.pop('signup_success', False)

    # Define the time periods you want to query
    time_periods = ['1day', '1month', '3months',
                    '6months', '1year', '5years', '10years', '20years']

    # Use a dictionary to store the results
    top_data = {}
    flop_data = {}

    # Get top data for each time period
    for time_period in time_periods:
        top_data[time_period] = get_top_data(
            'top', f'var_{time_period}', 10, '-')
        flop_data[time_period] = get_top_data('flop', f'var_{time_period}', 10)

    # Get all daily trade variations
    daily_var_data = get_top_data('all', f'var_1day', 100, '-')

    # Send data to template
    return render(
        request,
        'stocks/index.html',
        {
            'top_data': top_data,
            'flop_data': flop_data,
            'daily_var_data': daily_var_data,
            'success_messages': success_messages,
            'signup_success': signup_success,
        }
    )


# list of stocks views
# ------------------------------
# Decorator to restric access to the view  to register user only
@login_required
def stocks_list(request):
    """Get list of available stock prices with variances, pagination and search bar
    """
    # Get data from model and cached it
    daily_var_data = TradeVar.objects.all().order_by('symbol')
    daily_var_data = cache_data('daily_var_data_db', daily_var_data)

    # Get sorting field and order from html page
    sort_by = request.GET.get("sort_by", "symbol")
    sort_order = request.GET.get("sort_order")

    # Sort data
    if sort_order == "asc":
        daily_var_data = daily_var_data.order_by(sort_by)
    elif sort_order == "desc":
        daily_var_data = daily_var_data.order_by(f"-{sort_by}")

    # Get the search query from the GET request parameter
    search_query = request.GET.get('search', '')

    # Filter data based on search criteria
    if search_query:
        daily_var_data = daily_var_data.filter(symbol__icontains=search_query)

    # Set-up pagination indicating model on which to apply and the number ef element to display on one page
    paginator = Paginator(daily_var_data, 20)
    # Get page number through chain request page:number
    page = request.GET.get('page')

    # Get the specified page
    try:
        page_display = paginator.page(page)
    except PageNotAnInteger:
        page_display = paginator.page(1)
    except EmptyPage:
        page_display = paginator.page(paginator.num_pages)

    # Get page range around the current page
    page_range = paginator.get_elided_page_range(
        page_display.number, on_each_side=3)

    # switch sort order for next action on icon in template
    if sort_order == "asc":
        sort_order = "desc"
    elif sort_order == "desc":
        sort_order = "asc"
    else:
        sort_order = sort_order

    # Send data to template
    return render(
        request,
        'stocks/stocks_list.html',
        {
            'page_display': page_display,
            'page_range': page_range,
            'sort_order': sort_order,
            'sort_by': sort_by,
        }
    )


# Historical price view
# ------------------------------
# Decorator to restric access to the view  to register user only
@login_required
def stocks_evolution(request):
    """Get detailed view of daily trade data per ticker
    """

    # Query list of companies
    stocks = TradeVar.objects.values('symbol').order_by('symbol')

    # Get start, end date and company from the form
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    selected_stock = request.GET.get('stock', 'AAPL')

    # Query data from the database based on symbol
    data = DailyTrade.objects.filter(
        symbol=selected_stock.upper()).order_by('date_trade')

    # Filter data if start or end date
    if start:
        data = data.filter(date_trade__gte=start)
    if end:
        data = data.filter(date_trade__lte=end)

    # Pass the selected dates and companies as initial values to the form instead of restarting them
    form = StocksEvolutionForm(
        stocks, initial={'start': start, 'end': end, 'stock': selected_stock})

    # Create Plotly line chart
    fig = go.Figure(
        data=[go.Scatter(
            x=[trade.date_trade for trade in data],
            y=[trade.close_value for trade in data],
            mode='lines',
            line=dict(color=f'rgba({bs_primary_rgb}, 1)'),
            showlegend=False,
        )
        ]
    )

    # Adjust chart layout
    fig.update_layout(
        title={
            'text': f'Prix de clôture pour {selected_stock}',
            'font_size': 22,
            'xanchor': 'center',
            'x': 0.5
        },
        yaxis={
            'title': 'Prix (en $)',
            'gridcolor': f'rgba({bs_secondary_rgb}, 0.5 )'

        },
        xaxis={
            'showgrid': False
        },
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )

    # Convert chart to HTML
    chart = fig.to_html(full_html=False, default_height=600)

    return render(
        request,
        'stocks/stocks_evolution.html',
        {
            'chart': chart,
            "form": form,
            "selected_stock": selected_stock,
        }
    )


# Stock analysis view
# ------------------------------
# Decorator to restric access to the view  to register user only
@login_required
def stocks_analysis(request):
    """Get detailed analysis of stocks per ticker
    """

    # Query list of companies to be passed through in from
    stocks = TradeVar.objects.values('symbol').order_by('symbol')

    # Get the select stock
    selected_stock = request.GET.get('stock', 'AAPL')

    # Query data from the database based on symbol
    # As we retreive only one row of data, get() method is mandatory to access directly the values
    stock_var = TradeVar.objects.filter(
        symbol=selected_stock.upper()).get()
    stock_analysis_1year = StockAnalysis1Year.objects.filter(
        symbol=selected_stock.upper()).get()
    company_information = Company.objects.filter(
        symbol=selected_stock.upper()).get()
    income_statement = IncomeStatement.objects.filter(
        symbol=selected_stock.upper()).get()

    # Pass the selected company as initial value to the form
    form = StocksSelectionForm(stocks, initial={'stock': selected_stock})

    return render(
        request,
        'stocks/stocks_analysis.html',
        {
            "form": form,
            "selected_stock": selected_stock,
            "stock_var": stock_var,
            "stock_analysis_1year": stock_analysis_1year,
            "company_information": company_information,
            "income_statement": income_statement,
        }
    )


##########
# API
##########

# Generate API Key
# ------------------------------
@login_required
def generate_api_key(request):
    """Generate or update random API key for user and store it in apikey table
    """
    # Generate a tuple of API key value and True/false if the key exists
    api_key, created = ApiKey.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update the existing or newly created API key
        api_key.key = str(uuid.uuid4())
        api_key.save()
        # Display success message
        user = request.user
        user_name = user.username

        return render(request, 'stocks/api_key_get.html', {'api_key': api_key.key, 'user_name': user_name})

    return render(request, 'stocks/api_key_generate.html')


# API endpoint for dailytrade data
# ------------------------------
# Restrict API request to GET
@api_view(['GET'])
# Use custom API key for authentication through defined class
@authentication_classes([ApiKeyAuthentication])
# Check authentication
@permission_classes([IsAuthenticated])
def get_api_dailytrade(request):
    """Get dailytrade data from API
    """
    # Get arguments from urls (e.g.: api/dailytrade/?stock=AMZN&start=2022-12-20&end=2023-11-13)
    stock = request.GET.get('stock', '')
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')

    # Get data ordered by date descending
    queryset = DailyTrade.objects.all().order_by('-date_trade')

    # Filter stock if any
    if stock:
        queryset = queryset.filter(symbol=stock)

    # Filter data if start or end date
    if start:
        queryset = queryset.filter(date_trade__gte=start)
    if end:
        queryset = queryset.filter(date_trade__lte=end)

    serializer = DailyTradeSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Request to API with user interface
# ------------------------------
def api_daily_form(request):
    """
    User interface view to request API endpoint
    """

    # Initialize error message to None
    error_message = None

    # Query list of companies
    stocks = TradeVar.objects.values('symbol').order_by('symbol')

    if request.method == 'POST':
        # Pass through the list of companies separately from the form
        form = ApiDailyForm(stocks, request.POST)

        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            stock = form.cleaned_data['stock']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']

            # Request to the API endpoint using the provided API key and symbol
            # Use reverse to get the absolute URL dynamically and include start date and end date only if any
            url = request.build_absolute_uri(
                reverse('api-dailytrade')) + f'?stock={stock}'
            if start:
                url += f'&start={start}'
            if end:
                url += f'&end={end}'
            # include API key to the header of the request
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()
                # Format the JSON data with indentation for better readability
                data = json.dumps(data, indent=2)

                # Reset error_message to None for successful responses
                error_message = None

                # Return visualisation page
                if 'view_data' in request.POST:
                    return render(request, 'stocks/api_daily_result.html', {'data': data})

                # Return download
                if 'download_json' in request.POST:
                    response = HttpResponse(
                        data, content_type='application/json')
                    response['Content-Disposition'] = 'attachment; filename="result.json"'
                    return response

            # Return error message if unsuccessful
            else:
                # Handle unsuccessful response
                error_message = f"Erreur: {response.json().get('detail', 'Inconnue')}"
                return render(request, 'stocks/api_daily_form.html', {'form': form, 'error_message': error_message})

    # Display initial form when opening the page
    else:
        form = ApiDailyForm(stocks)

    return render(request, 'stocks/api_daily_form.html', {'form': form})
