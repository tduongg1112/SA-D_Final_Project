from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=120, required=False)
    customer_email = forms.EmailField(required=False)
    customer_phone = forms.CharField(max_length=20, required=False)
    shipping_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
