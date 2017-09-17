# from django.contrib.auth.models import User
from authentication.models import Profile
django.db.models import Q


query1 = Profile.objects.filter(role='mentor')
query2 = Profile.objects.filter(mentorship_areas__icontains='abuse')
query3 = Profile.objects.filter(mentorship_areas__icontains='career_counceling')
query4 = Profile.objects.filter(mentorship_areas__icontains='addictions')

intersection_items = query1.difference(query2, query3, query4)


#function that filters mentors depending on the mentorship_areas
class FindMyMentor():
    def __init__(self):
        self.mlist=[Profile.objects.values_list('id', 'mentorship_areas').filter(role='mentor')]
    def myMentor(self, **kwargs):
        return list(self.__iterMentor(**kwargs))
    def __iterMentor(self, **kwargs):
        return (mentor for mentor in self.mlist if mentor.match(**kwargs))


class Mentor001():
    def __init__(self, id, mentorship_areas):
        self.id = id
        self.mentorship_areas = mentorship_areas
    def __repr__(self):
        return "Mentor001(%d, %s)" % (self.id, self.mentorship_areas)
    def matchMentor(self, **kwargs):
        return all(getattr(self, key) == val for (key, val) in kwargs.items())