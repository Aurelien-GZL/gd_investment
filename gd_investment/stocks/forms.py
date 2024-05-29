from django import forms

# Form for stock evolution
#-------------------------------
class StocksEvolutionForm(forms.Form):
    """
    Selection of symbol and start and ending date for price evolution
    """
    start = forms.DateField(
        label='Début',
        widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        required=False
    )
    end = forms.DateField(
        label='Fin',
        widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        required=False
    )
    stock = forms.ChoiceField(
        label='Action',
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Init method call when an instance of the class is created
    def __init__(self, stocks, *args, **kwargs):
        """
        Constructor method of the form to set the choices for the stock fields

        Args:
        *args, **kwargs: any additional arguments
        """
        super(StocksEvolutionForm, self).__init__(*args, **kwargs)
        # Attach stock selection to the form field through comprehension list holding tuples
        self.fields['stock'].choices = [(stock['symbol'], stock['symbol']) for stock in stocks]


# Form for stock selection
#-------------------------------
class StocksSelectionForm(forms.Form):
    stock = forms.ChoiceField(
        label='Action',
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
        )

    # Init method call when an instance of the class is created
    def __init__(self, stocks, *args, **kwargs):
        """
        Constructor method of the form to set the choices for the stock fields

        Args:
        *args, **kwargs: any additional arguments
        """
        super(StocksSelectionForm, self).__init__(*args, **kwargs)
        # Attach stock selection to the form field through comprehension list holding tuples
        self.fields['stock'].choices = [(stock['symbol'], stock['symbol']) for stock in stocks]


# Form for API
#-------------------------------
class ApiDailyForm(StocksEvolutionForm):
    api_key = forms.CharField(
        label='Clé API',
        max_length=100,
        required=True,
        # type password input (characters hidden) with bootstrap class directly inside the field definition
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
