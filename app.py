from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/tugas2'
app.config['JWT_SECRET_KEY'] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

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
    password = db.Column(db.String(255), nullable=True)

class DataProdi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode_prodi = db.Column(db.String(5), nullable=True)
    nama_prodi = db.Column(db.String(100), nullable=True)

#REGISTER method 
@app.route('/register', methods=['POST'])
@jwt_required() 
def register():
    if request.method == 'POST':
        data = request.json
        nip = data['nip']
        nama_lengkap = data['nama_lengkap']
        prodi_id = data['prodi_id']
        password = data['password']

        # Periksa apakah NIP sudah ada dalam database
        test = DataDosen.query.filter_by(nip=nip).first()
        if test:
            return jsonify(message='That nip already exists'), 409
        else:
            # Enkripsi password
            hashed_password = generate_password_hash(password)
            # Tambahkan dosen baru ke database
            new_dosen = DataDosen(nip=nip, nama_lengkap=nama_lengkap, prodi_id=prodi_id, password=hashed_password)
            db.session.add(new_dosen)
            db.session.commit()
            # Buat token akses
            access_token = create_access_token(identity=nip)
            return jsonify(message='Dosen created successfully', access_token=access_token), 201
        
#LOGIN Method
@app.route('/login', methods=['POST'])
@jwt_required() 
def login():
    if request.is_json:
        nip = request.json['nip']
        password = request.json['password']
    else:
        nip = request.form['nip']
        password = request.form['password']

    dosen = DataDosen.query.filter_by(nip=nip).first()
    if dosen and check_password_hash(dosen.password.decode('utf-8'), password):
        access_token = create_access_token(identity=nip)
        return jsonify(message='Login Successful', access_token=access_token)
    else:
        return jsonify(message='Bad nip or Password'), 401


#POST Method
@app.route('/prodi', methods=['POST'])
@jwt_required() 
def create_prodi():
    if request.method == 'POST':
        data = request.json
        new_prodi = DataProdi(kode_prodi=data['kode_prodi'], nama_prodi=data['nama_prodi'])
        db.session.add(new_prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi created successfully'}), 201

@app.route('/dosen', methods=['POST'])
@jwt_required() 
def create_dosen():
    if request.method == 'POST':
        data = request.json
        new_dosen = DataDosen(nip=data['nip'], nama_lengkap=data['nama_lengkap'], prodi_id=data['prodi_id'])
        db.session.add(new_dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen created successfully'}), 201

@app.route('/document', methods=['POST'])
@jwt_required() 
def create_dokumen():
    if request.method == 'POST':
        data = request.json
        new_doc = DataDokumen(nip=data["nip"], type_dokumen=data["type_dokumen"], nama_dokumen=data["nama_dokumen"], nama_file=data["nama_file"])
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({"message": 'Document created successfully'})

#GET Method
#GET All
@app.route('/dosen', methods=['GET'])
@jwt_required() 
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
@jwt_required() 
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
@jwt_required() 
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
@jwt_required() 
def get_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        return jsonify({'nip': dosen.nip, 'nama_lengkap': dosen.nama_lengkap, 'prodi_id': dosen.prodi_id}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404

@app.route('/prodi/<int:id>', methods=['GET'])
@jwt_required() 
def get_prodi(id):
    prodi = DataProdi.query.get(id)
    if prodi:
        return jsonify({"id":prodi.id, 'kode_prodi': prodi.kode_prodi, 'nama_prodi': prodi.nama_prodi}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404

@app.route('/document/<int:id>', methods=['GET'])
@jwt_required() 
def get_document(id):
    doc = DataDokumen.query.get(id)
    if doc :
        return jsonify({'id:' : doc.id, 'type_document': doc.type_dokumen, 'nama_dokumen': doc.nama_dokumen, 'nama_file': doc.nama_file })
    else :
        return jsonify({'message': 'Document not found'}), 404

#PUT Method
@app.route('/prodi/<int:id>', methods=['PUT'])
@jwt_required() 
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
@jwt_required() 
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

@app.route('/document/<int:id>', methods=['PUT'])
@jwt_required() 
def update_dokumen(id):
    if request.method == 'PUT':
        data = request.json
        doc = DataDokumen.query.get(id)
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
@jwt_required() 
def delete_prodi(id):
    prodi = DataProdi.query.get(id)
    if prodi:
        db.session.delete(prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi deleted successfully'}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404

@app.route('/dosen/<nip>', methods=['DELETE'])
@jwt_required() 
def delete_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        db.session.delete(dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen deleted successfully'}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404

@app.route('/document/<int:id>', methods=['DELETE'])
@jwt_required()
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
