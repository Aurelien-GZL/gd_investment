from rest_framework.serializers import ModelSerializer
from .models import DailyTrade

# Define API serializer for Daily trade model
#------------------------------
class DailyTradeSerializer(ModelSerializer):
    """
    Serializer for daily trade model to convert data into native Python datatype 
    """
    class Meta:
        model=DailyTrade
        fields=[
            'symbol',
            'date_trade',
            'close_value',
            'volume'
        ]
    
