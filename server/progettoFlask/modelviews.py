from tkinter.ttk import Label

from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.model.template import ViewRowAction, EditRowAction, DeleteRowAction
from flask_login import current_user, login_required
from sqlalchemy import join
from wtforms import StringField, BooleanField, SelectField

import geolog
from models import db, buildings, User, professions
from werkzeug.routing import ValidationError

class ZoneAdmin(sqla.ModelView):
    can_edit=False
    column_exclude_list = ['id_zone','lat','lon']
    form_columns = (
        'city',
        'state',
    )
    def on_model_delete(self,zones):
        buildingsToCheck = db.session.query(buildings).filter_by(id_zone=zones.id_zone).first()
        if buildingsToCheck is not None:
            raise ValidationError('Sono presenti strutture assegnate a questa Zona')
    def is_accessible(self):
        return current_user.is_admin
    def on_model_change(self, form, zones,is_created):
        if geolog.isAddressValid(str(form.city.data)+","+str(form.state.data)):
            marker=geolog.getMarkerByType(str(form.city.data)+','+str(form.state.data),"administrative")
            zones.set_lat(marker["lat"])
            zones.set_lon(marker["lon"])
        else:
            raise ValidationError('Indirizzo non valido')



#inserire un super user che può dare grant di permessi
class UserAdmin(sqla.ModelView):
    column_list = ('username','profession','name','admin','super_user')
    column_exclude_list = ['id','password']
    can_create = False
    can_delete = False
    #column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    form_excluded_columns = ('id','dateOfBirth','password', 'profession', 'sex',)
    form_widget_args = {
        'username': {
            'disabled': True
        }
    }
    def is_accessible(self):
            return current_user.is_admin
    def get_list_row_actions(self):
        if current_user.is_authenticated and current_user.is_super:
            return (ViewRowAction(),EditRowAction())
        else:
            return ()
    def on_model_change(self, form, model, is_created):
        if is_created == False:
            if form.username.data == "Admin":
                raise ValidationError('Can\'t revoke permissions from Super User Admin')
            if form.super_user.data== True:
                model.admin=True
    #def get_query(self):
     #   return (self.session.query(User).join(professions,User.profession==professions.id_profession))
#TODO testing
#creazione,eliminazione e edit
class JobAdmin(sqla.ModelView):
    column_list = ('name','category')
    column_exclude_list = ['id_profession']
    form_columns = (
        'name',
        'category',)
    form_extra_fields = {
        'category': SelectField('Category', choices=[(0, 'Intrattenimento'),(1, 'Studio'),(2,'Ufficio'),(3, 'Manuale'),(4, 'Risorse umane'),(5, 'Altro')]),
    }

    def is_accessible(self):
        return current_user.is_admin
    def on_model_delete(self,job):
        users = db.session.query(User).filter_by(profession=job.id_profession).first()
        if users is not None:
            raise ValidationError('Sono presenti utenti assegnati a questa professione')




#TODO permessi di visione solo a admin e super user
#TODO convertire profession alla stringa
#TODO mettere il controllo d'inserimento della zona











class MyView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('admin/index.html')
class MyHomeView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        arg1 = 'Hello'
        return self.render('admin/index.html')
'''
#TODO testing inserimento, eliminazione e modifica



#creazione edifici

#grant permessi admin
#TODO gestione del digitaltwin per l'eliminazione delle stanze
#all'eliminazione togliamo pure i digital twin
#si blocca se ci sono sessioni attive
#alla creazione non viene creato nessun digital twin
#per la creazione possiamo assegnare una città già esistente o di poter inserire
#una città nuova
#modifica dell'indirizzo, con aggiornamento dei dati e controllo validità dell'indirizzo

class BuildingAdmin(sqla.ModelView):
    # Visible columns in the list view
    column_exclude_list = ['id_zone', 'id_building', 'lat','lon']
    form_excluded_columns = ('id_zone', 'id_building', 'lat','lon')
    # set the form fields to use
    #route = db.Column(db.String(100))
    #number = db.Column(db.String(100))
    #name = StringField('name')
    #form_columns = (
       # 'route',
       # 'number',
    #)
    form_extra_fields = {
        'City': StringField('City'),
        #'Number of rooms':IntegerField('Number of rooms'),
    }
    #def on_form_prefill(self, form, id):

    #aggiungere logica
    #se sessioni attive non s'inserisce nienete
    def on_model_delete(self, building):
        activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)
        activeRoom = db.session.query(rooms).filter_by(id_building=building.id_building and rooms.id_room.in_(activeSessionStates)).first()
        #freeBuildings = db.session.query(buildings).filter(buildings.id_building.in_(freeRoomsBuildings))
        if activeRoom is not None:
            raise ValidationError('Sono presenti sessioni attive questo Edificio')

    def is_accessible(self):
        # print(current_user.is_authenticated)
        return current_user.is_authenticated

    def on_model_change(self, form, zones, is_created):
        if geolog.isAddressValid(str(form.city.data) + "," + str(form.state.data)):
            marker = geolog.getMarkerByType(str(form.city.data) + ',' + str(form.state.data), "administrative")
            zones.set_lat(marker["lat"])
            zones.set_lon(marker["lon"])
        else:
            raise ValidationError('Indirizzo non valido')


#TODO testing
#TODO gestione del digitalTwin
#inserimento,modifica ed eliminazione stanze
#gestione del digital twin
class RoomAdmin(sqla.ModelView):
    form_excluded_columns = ('id_room','id_building')
    def on_form_prefill(self, form, id):
        with app.app_context():
            buildingsForForm = db.session.query(buildings)
            form.Buildings.choices = createABuildingtupleList(buildingsForForm)
    def scaffold_form(self):
        form = super(RoomAdmin, self).scaffold_form()
        with app.app_context():
            buildingsForForm = db.session.query(buildings)
            choices=createABuildingtupleList(buildingsForForm)
            form.Buildings = SelectField(u'Edificio',choices=choices)
        return form
    def on_model_delete(self, room):
        activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True,id_room=room.id_room)
        if activeSessionStates is not None:
            raise ValidationError('è presente una sessione attiva in questa stanza!')
#        else:
            #delete del digital twin
    def is_accessible(self):
        return current_user.is_authenticated
    def on_model_change(self, form, room, is_created):
        if not is_created:
            activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True, id_room=room.id_room)
            if activeSessionStates is not None:
                raise ValidationError('è presente una sessione attiva in questa stanza!')
            else:
                room.set_building(form.Buildings.data)
        else:
            room.set_building(form.Buildings.data)
            '''