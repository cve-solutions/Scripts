import rrdtool
import numpy as np
from scipy.stats import linregress
from datetime import datetime, timedelta

# Paramètres
rrd_path = 'chemin/base.rrd'
ds_name = 'datasource'
cf = 'AVERAGE'
start, end = 'end-30d', 'now'

# Extraction des données RRD
timestamps, data = rrdtool.fetch(rrd_path, cf, '--start', start, '--end', end)

dates = [datetime.fromtimestamp(ts) for ts in range(timestamps[0], timestamps[1], timestamps[2])]
valeurs = [val[ds_name] if val[ds_name] else 0 for val in data]

# Filtrer les données valides
dates, valeurs = zip(*[(d, v) for d, v in zip(dates, valeurs) if v])

jours_depuis_debut = np.array([(d - dates[0]).total_seconds() / 86400 for d in dates])
valeurs = np.array(valeurs)

# Régression linéaire
pente, intercept, *_ = linregress(jours_depuis_debut, valeurs)

# Prédiction 80%
jours_cible = (80 - intercept) / pente
date_cible = dates[0] + timedelta(days=jours_cible)

# Générer le fichier PHP
with open('graphique.php', 'w') as php:
    php.write(f"""
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
    <title>Graphique avec Régression Linéaire</title>
</head>
<body>
<canvas id='myChart' width='800' height='400'></canvas>
<script>
    const ctx = document.getElementById('myChart').getContext('2d');
    const dates = { [d.strftime('%Y-%m-%d') for d in dates] };
    const valeurs = { valeurs.tolist() };
    const regression = dates.map((_, idx) => ({intercept:.4f} + idx * {pente:.4f}));

    const data = {{
        labels: dates,
        datasets: [
            {{
                type: 'bar',
                label: 'Valeurs %',
                data: valeurs,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }},
            {{
                type: 'line',
                label: 'Régression',
                data: regression,
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false
            }},
            {{
                type: 'scatter',
                label: 'Atteinte 80%',
                data: [{{ x: '{date_cible.strftime('%Y-%m-%d')}', y: 80 }}],
                backgroundColor: 'rgba(255, 206, 86, 1)',
                pointRadius: 8
            }}
        ]
    }};

    new Chart(ctx, {{
        data,
        options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
    }});
</script>
</body>
</html>
    """)

print(f"Page PHP générée avec succès. Valeur de 80% prévue pour le {date_cible.strftime('%d/%m/%Y %H:%M:%S')}")
