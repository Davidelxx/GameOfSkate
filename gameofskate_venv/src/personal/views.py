from django.shortcuts import render, redirect


def no_login_view(request):
	context = {}
	user = request.user
	if user.is_authenticated:
		return redirect('cuenta/'+str(user.pk))

	return render(request, "personal/home.html", context)