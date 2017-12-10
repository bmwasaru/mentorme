from django.contrib.auth.models import User
from authentication.models import Connection

users = User.objects.all()
connections = Connection.objects.filter(mentor=1)

for con in connections:
	mentees = values_list(con.user.id)
	print(mentees)

connections = Connection.objects.values_list('user').distinct().filter(mentor=1)

for con in connections:
	for item in con:
		User.objects.filter(id=item)

connections = Connection.objects.values('user').distinct().filter(mentor=1)

for con in connections:
	con.user