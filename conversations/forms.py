from django import forms


class AddCommentForm(forms.Form):
    """ AddCommentForm Definition """

    message = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"placeholder": "Send a message"})
    )
