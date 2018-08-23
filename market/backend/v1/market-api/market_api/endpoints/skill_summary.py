"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict

from flask import request
import requests as service_request

from selene_util.api import SeleneBaseView, AuthorizationError

UNDEFINED = 'Undefined'


class SkillSummaryView(SeleneBaseView):
    def __init__(self):
        super(SkillSummaryView, self).__init__()
        self.response_data = defaultdict(list)
        self.search_term = None

    def get(self):
        """Handle a HTTP GET request."""
        try:
            self._authenticate()
        except AuthorizationError:
            pass
        self._build_response()

        return self.response

    def _build_response_data(self):
        """Build the data to include in the response."""
        self.skill_service_response = service_request.get(
            self.base_url + '/skill/all'
        )
        if request.query_string:
            query_string = request.query_string.decode()
            self.search_term = query_string.lower().split('=')[1]
        self._reformat_skills()
        self._sort_skills()

    def _reformat_skills(self):
        """Build the response data from the skill service response"""
        for skill in self.skill_service_response.json():
            skill_summary = dict(
                author=skill['author'],
                id=skill['id'],
                title=skill['title'],
                summary=skill['summary'],
                triggers=skill['triggers']
            )
            search_term_match = (
                self.search_term is None or
                self.search_term in skill['title'].lower()
            )
            if search_term_match:
                skill_category = skill.get('category', UNDEFINED)
                self.response_data[skill_category].append(skill_summary)

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        for skill_category, skills in self.response_data.items():
            sorted_skills = sorted(skills, key=lambda skill: skill['title'])
            self.response_data[skill_category] = sorted_skills