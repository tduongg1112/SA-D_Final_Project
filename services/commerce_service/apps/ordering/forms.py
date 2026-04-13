from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=120)
    customer_email = forms.EmailField()
    customer_phone = forms.CharField(max_length=20)
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
