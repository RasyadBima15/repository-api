from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_repositori'
db = SQLAlchemy(app)

#class models
class DataDokumen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(30), db.ForeignKey('data_dosen.nip'), nullable=True)
    type_dokumen = db.Column(db.Enum('file', 'url'), nullable=False)
    nama_dokumen = db.Column(db.String(255), nullable=True)
    nama_file = db.Column(db.String(255), nullable=True)
class DataDosen(db.Model):
    nip = db.Column(db.String(30), primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=True)
    prodi_id = db.Column(db.Integer, db.ForeignKey('data_prodi.id'), nullable=True)
class DataProdi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode_prodi = db.Column(db.String(5), nullable=True)
    nama_prodi = db.Column(db.String(100), nullable=True)

#POST Method
@app.route('/prodi', methods=['POST'])
def create_prodi():
    if request.method == 'POST':
        data = request.json
        new_prodi = DataProdi(kode_prodi=data['kode_prodi'], nama_prodi=data['nama_prodi'])
        db.session.add(new_prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi created successfully'}), 201
@app.route('/dosen', methods=['POST'])
def create_dosen():
    if request.method == 'POST':
        data = request.json
        new_dosen = DataDosen(nip=data['nip'], nama_lengkap=data['nama_lengkap'], prodi_id=data['prodi_id'])
        db.session.add(new_dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen created successfully'}), 201
@app.route('/document', methods=['POST'])
def create_dokumen():
    if request.method == 'POST':
        data = request.json
        new_doc = DataDokumen(nip=data["nip"], type_dokumen=data["type_dokumen"], nama_dokumen=data["nama_dokumen"], nama_file=data["nama_file"])
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({"message": 'Document created succusfully'})
    
#GET Method
#GET All
@app.route('/dosen', methods=['GET'])
def get_all_dosen():
    dosen = DataDosen.query.all()
    if dosen:
        result = []
        for d in dosen:
            result.append({'nip': d.nip, 'nama_lengkap': d.nama_lengkap, 'prodi_id': d.prodi_id})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No dosen found'}), 404
@app.route('/prodi', methods=['GET'])
def get_all_prodi():
    prodi_list = DataProdi.query.all()
    if prodi_list:
        result = []
        for prodi in prodi_list:
            result.append({'id':prodi.id, 'kode_prodi': prodi.kode_prodi, 'nama_prodi': prodi.nama_prodi})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No program studi found'}), 404
@app.route('/document', methods=['GET'])
def get_all_documen():
    dokumen = DataDokumen.query.all()
    if dokumen:
        result = []
        for d in dokumen:
            result.append({"id":d.id, 'nip': d.nip, 'type_dokumen': d.type_dokumen, 'nama_dokumen': d.nama_dokumen, 'nama_file': d.nama_file})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No documents found'}), 404
#Get By Parameter
@app.route('/dosen/<nip>', methods=['GET'])
def get_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        return jsonify({'nip': dosen.nip, 'nama_lengkap': dosen.nama_lengkap, 'prodi_id': dosen.prodi_id}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404
@app.route('/prodi/<int:kode_prodi>', methods=['GET'])
def get_prodi(kode_prodi):
    prodi = DataProdi.query.get(kode_prodi)
    if prodi:
        return jsonify({"id":prodi.id, 'kode_prodi': prodi.kode_prodi, 'nama_prodi': prodi.nama_prodi}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404
@app.route('/document/<id>', methods=['GET'])
def get_document(id):
    doc = DataDokumen.query.get(id)
    if doc :
        return jsonify({'id:' : doc.id, 'type_document': doc.type_dokumen, 'nama_dokumen': doc.nama_dokumen, 'nama_file': doc.nama_dokumen })
    else :
        return jsonify({'message': 'Document not found'}), 404

#PUT Method
@app.route('/prodi/<int:id>', methods=['PUT'])
def update_prodi(id):
    data = request.json
    prodi = DataProdi.query.get(id)
    if prodi:
        prodi.nama_prodi = data['nama_prodi']
        prodi.kode_prodi = data['kode_prodi']
        db.session.commit()
        return jsonify({'message': 'Prodi updated successfully'}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404
@app.route('/dosen/<nip>', methods=['PUT'])
def update_dosen(nip):
    if request.method == 'PUT':
        data = request.json
        dosen = DataDosen.query.get(nip)
        if dosen:
            dosen.nama_lengkap = data['nama_lengkap']
            dosen.prodi_id = data['prodi_id']
            db.session.commit()
            return jsonify({'message': 'Dosen updated successfully'}), 200
        else:
            return jsonify({'message': 'Dosen not found'}), 404
@app.route('/document/<nip>', methods=['PUT'])
def update_dokumen(nip):
    if request.method == 'PUT':
        data = request.json
        doc = DataDokumen.query.get(nip)
        if doc:
            doc.nip = data['nip']
            doc.type_dokumen = data['type_dokumen']
            doc.nama_dokumen = data['nama_dokumen']
            doc.nama_file = data['nama_file']
            db.session.commit()
            return jsonify({'message': 'Document updated successfully'}), 200
        else:
            return jsonify({'message': 'Document not found'}), 404
        
#DELETE Method
@app.route('/prodi/<int:id>', methods=['DELETE'])
def delete_prodi(id):
    prodi = DataProdi.query.get(id)
    if prodi:
        db.session.delete(prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi deleted successfully'}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404
@app.route('/dosen/<nip>', methods=['DELETE'])
def delete_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        db.session.delete(dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen deleted successfully'}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404
@app.route('/document/<int:id>', methods=['DELETE'])
def delete_dokumen(id):
    doc = DataDokumen.query.get(id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'message': 'Document not found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)