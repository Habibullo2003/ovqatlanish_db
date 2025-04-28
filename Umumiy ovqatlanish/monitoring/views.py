from django.shortcuts import render
from .forms import CSVForm
from .monitoring import monitoring

def index(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file']

        # Restoran monitoringini bajarish
        df, image = monitoring(csv_file)

        return render(request, 'monitoring/monitoring.html', {
            'form': CSVForm(),
            'data': df.to_html(classes='table table-striped'),
            'image': image
        })

    else:
        form = CSVForm()
        return render(request, 'monitoring/monitoring.html', {'form': form})
