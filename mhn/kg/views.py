from flask import (Blueprint, render_template)
from mhn.api.models import (Sensor)
from mhn.auth import login_required

kg = Blueprint('kg', __name__, url_prefix='/kg')

@kg.route('/kippo_graph/', methods=['GET'])
@login_required
def kippo_graph():
        graphs = {'top_10_passwords':'Top 10 Passwords Attempted',
                  'top_10_usernames':'Top 10 Usernames Attempted',
                  'top_10_combinations':'Top 10 Username-Password Combinations',
                  'success_ratio':'Overall Success Ratio',
                  'number_connections_per_ip':'Number of Connections per Unique IP (Top 10)',
                  'successful_logins_from_same_ip': 'Successful Logins from Same IP (Top 20)',
                  'top_10_ssh_clients': 'Top 10 SSH Clients',
                  'top_10_overall_input': 'Top 10 Input (Overall)',
                  'top_10_successful_input': 'Top 10 Successful Input',
                  'top_10_failed_input': 'Top 10 Failed Input',
                  'most_successful_logins_per_day': 'Most Successful Logins per day (Top 20)',
                  'successes_per_day': 'Successes per day',
                  'successes_per_week': 'Successes per Week',
                  'most_probes_per_day': 'Most Probes per day (Top 20)',
                  'probes_per_day': 'Probes per day',
                  'probes_per_week': 'Probes per Week',
                  'human_activity_busiest_days': 'Human Activity busiest days (Top 20)',
                  'human_activity_per_day': 'Human Activity per day',
                  'human_activity_per_week': 'Human Activity per Week', }
        sensors = Sensor.query.filter_by(honeypot='kippo').all()
        data = {}
        for sr in sensors:
                subdata = []
                for name, title in graphs.iteritems():
                        image_set = {}
                        image_set['url'] = name + '_kippo_' + sr.uuid.replace('-', '_') + '.png'
                        image_set['thumb'] = name + '_kippo_' + sr.uuid.replace('-', '_') + '_th' + '.png'
                        image_set['title'] = title
                        subdata.append(image_set)
                data[sr.name] = subdata
        return render_template('kg/stats.html', data=data)

__author__ = 'mercolino'
