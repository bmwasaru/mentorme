from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from questions.models import Question


@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')

        try:
            search_type = request.GET.get('type')
            if search_type not in ['questions', 'users']:
                search_type = 'questions'

        except Exception:
            search_type = 'questions'

        count = {}
        results = {'questions': Question.objects.filter(
            Q(title__icontains=querystring) | Q(
                description__icontains=querystring)), 'users': User.objects.filter(
            Q(username__icontains=querystring) | Q(
                first_name__icontains=querystring) | Q(
                last_name__icontains=querystring))}
        count['questions'] = results['questions'].count()
        count['users'] = results['users'].count()

        return render(request, 'search/results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        return render(request, 'search/search.html', {'hide_search': True})
