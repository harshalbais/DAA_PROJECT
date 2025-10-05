from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# --------------------------------------------------------
# In-memory storage for demo purposes
# --------------------------------------------------------
patients = []


# --------------------------------------------------------
# Greedy Scheduling Algorithm (Activity Selection)
# --------------------------------------------------------
def greedy_schedule(patients_list):
    # Sort patients by end time
    sorted_patients = sorted(patients_list, key=lambda x: x[2])
    scheduled = []
    last_end = -1

    for patient in sorted_patients:
        name, start, end = patient
        if start >= last_end:
            scheduled.append(patient)
            last_end = end
    return scheduled


# --------------------------------------------------------
# API Endpoints
# --------------------------------------------------------
@app.route('/api/patients', methods=['GET'])
def get_patients():
    return jsonify([{'name': p[0], 'start': p[1], 'end': p[2]} for p in patients])


@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json or {}
    name = data.get('name', '').strip()

    try:
        start = int(data.get('start'))
        end = int(data.get('end'))
    except Exception:
        return jsonify({'error': 'Start and End must be integers'}), 400

    if not name or start >= end:
        return jsonify({'error': 'Invalid name or time values'}), 400

    patients.append((name, start, end))
    return jsonify({'status': 'ok'}), 201


@app.route('/api/clear', methods=['POST'])
def clear_patients():
    patients.clear()
    return jsonify({'status': 'cleared'})


@app.route('/api/auto', methods=['POST'])
def auto_generate():
    patients.clear()
    names = ["Ram", "Shyam", "Sita", "Gita", "Aman", "Pooja", "Vikas", "Rani"]
    for i in range(8):
        name = random.choice(names) + str(i + 1)
        start = random.randint(1, 8)
        end = start + random.randint(1, 4)
        patients.append((name, start, end))
    return jsonify({'status': 'generated', 'count': len(patients)})


@app.route('/api/schedule', methods=['GET'])
def schedule():
    if not patients:
        return jsonify({'error': 'No patients'}), 400
    scheduled = greedy_schedule(patients)
    return jsonify([{'name': p[0], 'start': p[1], 'end': p[2]} for p in scheduled])


# --------------------------------------------------------
# Frontend (Single-File UI using render_template_string)
# --------------------------------------------------------
INDEX_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Hospital Patient Appointment Scheduler</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    :root { --accent: #0d6efd; }
    body {
      background: linear-gradient(180deg, #f7fbff, #ffffff);
      font-family: Inter, system-ui, Segoe UI, Roboto, "Helvetica Neue", Arial;
    }
    .card { border: none; box-shadow: 0 6px 20px rgba(13,110,253,0.08); }
    .muted { color: #6c757d; }
    .patient-item {
      display: flex; justify-content: space-between;
      align-items: center; padding: 10px; border-radius: 8px;
    }
    .patient-item + .patient-item { margin-top: 8px; }
    .pill {
      background: #f1f5ff; padding: 6px 10px; border-radius: 999px; font-weight: 600;
    }
    .btn-primary { background: var(--accent); border: none; }
    pre {
      background: #0b1220; color: #dff3ff; padding: 12px; border-radius: 8px;
    }
    @media (min-width:900px) {
      .layout { display: grid; grid-template-columns: 420px 1fr; gap: 32px; }
    }
  </style>
</head>

<body>
  <div class="container py-4">
    <h2 class="mb-1">Hospital Patient Appointment Scheduler</h2>
    <p class="muted">Greedy (activity selection) scheduling with a responsive modern UI.</p>

    <div class="card p-3 mt-4 layout">
      <div>
        <h5 class="mb-3">Add Patient</h5>
        <div class="mb-2">
          <label class="form-label">Name</label>
          <input id="name" class="form-control" placeholder="Patient name" />
        </div>

        <div class="row g-2 mb-3">
          <div class="col">
            <label class="form-label">Start Time</label>
            <input id="start" type="number" class="form-control" placeholder="e.g. 1" />
          </div>
          <div class="col">
            <label class="form-label">End Time</label>
            <input id="end" type="number" class="form-control" placeholder="e.g. 3" />
          </div>
        </div>

        <div class="d-flex gap-2 mb-3">
          <button id="addBtn" class="btn btn-primary">Add Patient</button>
          <button id="autoBtn" class="btn btn-outline-secondary">Auto Generate</button>
          <button id="clearBtn" class="btn btn-outline-danger">Clear All</button>
        </div>

        <h6 class="mt-3">All Patients</h6>
        <div id="patientsList" class="mt-2"></div>
      </div>

      <div>
        <div class="d-flex justify-content-between align-items-center">
          <h5>Scheduling</h5>
          <div>
            <button id="runSchedule" class="btn btn-success">Run Scheduling</button>
          </div>
        </div>

        <div class="mt-3">
          <h6>Scheduled Patients</h6>
          <div id="scheduledList" class="mt-2"></div>
        </div>

        <div class="mt-4">
          <h6>Raw Data (JSON)</h6>
          <pre id="raw" class="small">[]</pre>
        </div>
      </div>
    </div>

    <footer class="text-center text-muted mt-4">
      Tip: Use small integer times for demo (e.g. 1..12). This is an in-memory demo server.
    </footer>
  </div>

  <script>
    async function api(path, method='GET', body=null){
      const opts = { method, headers: {'Content-Type':'application/json'} };
      if (body) opts.body = JSON.stringify(body);
      const res = await fetch(path, opts);
      if (!res.ok){
        const err = await res.json().catch(()=>({error:'Unknown error'}));
        throw err;
      }
      return res.json();
    }

    const patientsList = document.getElementById('patientsList');
    const scheduledList = document.getElementById('scheduledList');
    const raw = document.getElementById('raw');

    function renderPatients(data){
      patientsList.innerHTML = '';
      data.forEach(p => {
        const item = document.createElement('div');
        item.className = 'patient-item bg-white';
        item.innerHTML = `<div><strong>${p.name}</strong><div class='muted'>Start: ${p.start} • End: ${p.end}</div></div><div class='pill'>${p.start}-${p.end}</div>`;
        patientsList.appendChild(item);
      });
      raw.textContent = JSON.stringify(data, null, 2);
    }

    function renderScheduled(data){
      scheduledList.innerHTML = '';
      if (data.length === 0){
        scheduledList.innerHTML = '<div class="muted">No scheduled patients</div>';
        return;
      }
      data.forEach((p, i) => {
        const item = document.createElement('div');
        item.className = 'patient-item bg-white';
        item.innerHTML = `<div><strong>${i+1}. ${p.name}</strong><div class='muted'>Start: ${p.start} • End: ${p.end}</div></div><div class='pill'>Slot ${i+1}</div>`;
        scheduledList.appendChild(item);
      });
    }

    async function loadPatients(){
      try {
        const data = await api('/api/patients');
        renderPatients(data);
      } catch (e) { console.error(e); }
    }

    document.getElementById('addBtn').addEventListener('click', async ()=>{
      const name = document.getElementById('name').value;
      const start = document.getElementById('start').value;
      const end = document.getElementById('end').value;
      try {
        await api('/api/patients','POST',{name,start,end});
        document.getElementById('name').value='';
        document.getElementById('start').value='';
        document.getElementById('end').value='';
        await loadPatients();
      } catch (err) { alert(err.error || 'Failed to add'); }
    });

    document.getElementById('autoBtn').addEventListener('click', async ()=>{
      try {
        await api('/api/auto','POST');
        await loadPatients();
      } catch (e) { console.error(e); }
    });

    document.getElementById('clearBtn').addEventListener('click', async ()=>{
      if(!confirm('Clear all patients?')) return;
      await api('/api/clear','POST');
      await loadPatients();
      renderScheduled([]);
    });

    document.getElementById('runSchedule').addEventListener('click', async ()=>{
      try {
        const data = await api('/api/schedule');
        renderScheduled(data);
      } catch (err) { alert(err.error || 'Failed to schedule'); }
    });

    // Initial load
    loadPatients();
  </script>
</body>
</html>
'''

# --------------------------------------------------------
# Flask Route to Render UI
# --------------------------------------------------------
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
