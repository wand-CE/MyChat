from django import forms

from groups.models import GroupNames


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = GroupNames
        fields = ['name', 'photo']
        labels = {
            "name": 'Nome do Grupo',
            "photo": 'Foto do Grupo',
        }

    def clean(self):
        if not len(self.cleaned_data['name'].strip()):
            raise forms.ValidationError({"name": "Empty Group Name"})
        return self.cleaned_data
