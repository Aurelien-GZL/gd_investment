from django.core.exceptions import ValidationError

def contains_letter(value):
    """Check value contains at least one letter
    """
    # Goes through each value character and check if it is a letter
    if not any(char.isalpha() for char in value):
        raise ValidationError('Doit contenir au moins une lettre.', code='value_no_letter')
    

def contains_number(value):
    """Check value contains at least one number
    """
    # Goes through each value character and check if it is a letter
    if not any(char.isdigit() for char in value):
        raise ValidationError('Doit contenir au moins un chiffre.', code='value_no_number')
    

def contains_special_character(value):
    """Check if the value contains a special character"""
    special_characters = "!@#$%^&*()_+[]{}|;':,.<>?/"
    
    if not any(char in special_characters for char in value):
        raise ValidationError('Doit contenir au moins un caratère spécial: !@#$%^&*()_+[]{}|;\':,.<>?/', code='value_no_special_character')