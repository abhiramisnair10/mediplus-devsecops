from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from mediplus.models import user_details, doctor_details
from user_app.models import appointment_details


@require_GET
def userview(request):
    data = user_details.objects.all()
    return render(request, 'userview.html', {'userdata': data})


@require_POST
def userdelete(request, id):
    data = get_object_or_404(user_details, pk=id)
    data.delete()
    return redirect(userview)


@require_GET
def userupdate(request, id):
    data = get_object_or_404(user_details, pk=id)
    return render(request, 'userupdate.html', {'result': data})


@require_POST
def userupdates(request, id):
    data = get_object_or_404(user_details, id=id)

    data.username = request.POST.get("username")
    data.useremail = request.POST.get("useremail")
    data.userphone = request.POST.get("userphone")

    if "userphoto" in request.FILES:
        data.userphoto = request.FILES["userphoto"]

    data.save()
    return redirect(userview)


@require_http_methods(["GET", "POST"])
def doctor_register(request):
    if request.method == "POST":
        data = doctor_details(
            docphoto=request.FILES.get("docphoto"),
            docname=request.POST.get("docname"),
            docspeciallization=request.POST.get("docspeciallization"),
            docpayment=request.POST.get("docpayment"),
            doctiming=request.POST.get("doctiming")
        )
        data.save()
        return redirect(doctor_view)

    return render(request, 'doctor_register.html')


@require_GET
def doctor_view(request):
    data = doctor_details.objects.all()
    return render(request, 'doctor_view.html', {'doctordata': data})


@require_POST
def doctordelete(request, id):
    data = get_object_or_404(doctor_details, pk=id)
    data.delete()
    return redirect(doctor_view)


@require_GET
def doctorupdate(request, id):
    data = get_object_or_404(doctor_details, pk=id)
    return render(request, 'doctorupdate.html', {'result': data})


@require_POST
def doctorupdates(request, id):
    data = get_object_or_404(doctor_details, id=id)

    if "docphoto" in request.FILES:
        data.docphoto = request.FILES["docphoto"]

    data.docname = request.POST.get("docname")
    data.docspeciallization = request.POST.get("docspeciallization")
    data.docpayment = request.POST.get("docpayment")
    data.doctiming = request.POST.get("doctiming")

    data.save()
    return redirect(doctor_view)


@require_GET
def adminapp_view(request):
    data = appointment_details.objects.all()
    return render(request, 'adminapp_view.html', {'result': data})


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "POST":
        useremail = request.POST.get("useremail")
        userpassword = request.POST.get("userpassword")

        try:
            user = user_details.objects.get(
                useremail=useremail,
                userpassword=userpassword
            )
            request.session['uid'] = user.pk
            return redirect('home')

        except user_details.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Invalid email or password'
            })

    return render(request, 'login.html')