from flask_restful import Resource, fields, marshal_with


class Home(Resource):
    def get(self):
        return {"message": "medico api"}
