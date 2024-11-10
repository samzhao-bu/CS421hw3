from django.views.generic import ListView, DetailView
from .models import Voter
import plotly.express as px
import plotly.io as pio
import pandas as pd

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unique_parties'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        party = self.request.GET.get('party', None)
        min_dob = self.request.GET.get('min_dob', None)
        max_dob = self.request.GET.get('max_dob', None)
        voter_score = self.request.GET.get('score', None)
        voted_in_v20state = self.request.GET.get('v20state', None)

        if party:
            queryset = queryset.filter(party_affiliation=party)
        if min_dob:
            queryset = queryset.filter(date_of_birth__gte=min_dob)
        if max_dob:
            queryset = queryset.filter(date_of_birth__lte=max_dob)
        if voter_score:
            queryset = queryset.filter(voter_score=voter_score)
        if voted_in_v20state is not None:
            voted = True if voted_in_v20state == 'Y' else False
            queryset = queryset.filter(v20state=voted)

        return queryset

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'


class VoterGraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'
    paginate_by = 100  # Optional, depending on whether you want pagination on this page

    def get_queryset(self):
        queryset = super().get_queryset()
        party = self.request.GET.get('party')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('score')
        v20state = self.request.GET.get('v20state', None)

        if party:
            queryset = queryset.filter(party_affiliation=party)
        if min_dob:
            queryset = queryset.filter(date_of_birth__gte=min_dob)
        if max_dob:
            queryset = queryset.filter(date_of_birth__lte=max_dob)
        if voter_score:
            queryset = queryset.filter(voter_score=voter_score)
        if v20state == 'Y':
            queryset = queryset.filter(v20state=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        df = pd.DataFrame(list(self.get_queryset().values()))
        context.update({
            'birth_histogram': self.create_histogram(df, 'date_of_birth', "Distribution of Voters by Year of Birth"),
            'party_pie_chart': self.create_pie_chart(df, 'party_affiliation', "Distribution by Party Affiliation"),
            'elections_bar_chart': self.create_participation_chart(df),
            'unique_parties': Voter.objects.values_list('party_affiliation', flat=True).distinct()
        })
        return context

    def create_histogram(self, df, column, title):
        fig = px.histogram(df, x=column, title=title)
        return pio.to_html(fig, full_html=False)

    def create_pie_chart(self, df, column, title):
        fig = px.pie(df, names=column, title=title)
        return pio.to_html(fig, full_html=False)

    def create_participation_chart(self, df):
        data = {election: df[election].sum() for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']}
        fig = px.bar(x=list(data.keys()), y=list(data.values()), title="Participation in Recent Elections")
        return pio.to_html(fig, full_html=False)
