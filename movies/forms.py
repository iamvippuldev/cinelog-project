from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Review

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })


RATING_CHOICES = [
    (5.0, "★★★★★ (5.0 - Masterpiece)"),
    (4.5, "★★★★½ (4.5 - Excellent)"),
    (4.0, "★★★★☆ (4.0 - Great)"),
    (3.5, "★★★½☆ (3.5 - Very Good)"),
    (3.0, "★★★☆☆ (3.0 - Good)"),
    (2.5, "★★½☆☆ (2.5 - Average)"),
    (2.0, "★★☆☆☆ (2.0 - Poor)"),
    (1.5, "★½☆☆☆ (1.5 - Bad)"),
    (1.0, "★☆☆☆☆ (1.0 - Terrible)"),
]


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=float,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rating",
    )

    class Meta:
        model = Review
        fields = ["rating", "review_text", "watched_date"]
        widgets = {
            "review_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Share your thoughts on the cinematography, direction, performances, themes, or standout moments...",
                "style": "min-height: 130px; resize: vertical;",
            }),
            "watched_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }
        labels = {
            "review_text": "Review",
            "watched_date": "Date Watched",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["review_text"].required = False
        self.fields["watched_date"].required = False

    def clean_rating(self):
        val = self.cleaned_data.get("rating")
        try:
            return float(val)
        except (ValueError, TypeError):
            raise forms.ValidationError("Please select a valid rating.")


from .models import Profile


class EditProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="First Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Last Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    avatar = forms.ImageField(
        required=False,
        label="Profile Picture",
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "id": "id_avatar",
        }),
    )
    avatar_url = forms.URLField(
        max_length=500,
        required=False,
        label="Or Avatar Image URL",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "https://example.com/avatar.jpg"}),
    )
    bio = forms.CharField(
        max_length=500,
        required=False,
        label="Bio",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Write a short bio about yourself and your film taste...",
            "style": "resize: vertical;",
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['username'].initial = self.user.username
            if hasattr(self.user, 'profile'):
                self.fields['avatar_url'].initial = self.user.profile.avatar_url
                self.fields['bio'].initial = self.user.profile.bio

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        if self.user and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self):
        if not self.user:
            return None
        self.user.first_name = self.cleaned_data.get('first_name', '').strip()
        self.user.last_name = self.cleaned_data.get('last_name', '').strip()
        new_username = self.cleaned_data.get('username', '').strip()
        self.user.username = new_username
        self.user.save()

        profile, _ = Profile.objects.get_or_create(user=self.user)
        avatar_file = self.cleaned_data.get('avatar')
        if avatar_file:
            profile.avatar = avatar_file
        avatar_url = self.cleaned_data.get('avatar_url', '').strip()
        if avatar_url:
            profile.avatar_url = avatar_url
        profile.bio = self.cleaned_data.get('bio', '').strip()
        profile.save()
        return self.user


