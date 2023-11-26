from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, SubmitField, StringField, PasswordField, validators, HiddenField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, Optional
from app.models import User,System
from app import bcrypt

def UsernameUnique(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user:
        raise ValidationError("This username is already taken")

def SystemUnique(form, field):
    system = System.query.filter_by(name=field.data).first()
    if system:
        raise ValidationError("A system with this name already exists.")


class RegisterForm(FlaskForm):
    #todo limit field lengths?
    username = StringField("Username*", validators=[DataRequired(), UsernameUnique], render_kw={'autofocus': True})
    first_name = StringField("First name*", validators=[DataRequired()])
    last_name = StringField("Last name*", validators=[DataRequired()])
    password = PasswordField("Password*", validators=[DataRequired()])
    passwordConfirm = PasswordField("Confirm password*", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate(self, extra_validators=None):
        valid = super(RegisterForm, self).validate(extra_validators)
        if not valid:
            return False

        if self.password.data == self.passwordConfirm.data:
            return True

        self.passwordConfirm.errors.append('Passwords do not match.')
        return False

class KPIEditForm(FlaskForm):
    kpi_name = StringField("Name*", validators=[DataRequired()], render_kw={'autofocus': True})
    kpi_description = TextAreaField("Description")
    parameter = SelectField("Parameter*", validators=[DataRequired()], coerce=int)
    lower_limit = FloatField("Lower limit", validators=[Optional()])
    upper_limit = FloatField("Upper limit", validators=[Optional()])
    submit = SubmitField("Save")

    def validate(self, extra_validators=None):
        valid = super(KPIEditForm, self).validate(extra_validators)
        if not valid:
            return False

        if self.lower_limit.data == None and self.upper_limit.data == None:
            self.lower_limit.errors.append("At least one limit has to be specified.")
            self.upper_limit.errors.append("At least one limit has to be specified.")
            return False

        if self.lower_limit.data != None and self.upper_limit.data != None and self.lower_limit.data > self.upper_limit.data:
            self.lower_limit.errors.append("The lower limit cannot be higher than the upper limit.")
            self.upper_limit.errors.append("The upper limit cannot be lower than the lower limit.")
            return False

        return True

class LoginForm(FlaskForm):
    #todo limit field lengths?
    username = StringField("Username*", validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField("Password*", validators=[DataRequired()])
    submit = SubmitField("Log in")

    def validate(self, extra_validators=None):
        valid = super(LoginForm, self).validate(extra_validators)
        if not valid:
            return False

        user = User.query.filter_by(username=self.username.data).first()

        if user and bcrypt.check_password_hash(user.hashed_password,self.password.data):
            return True

        self.password.errors.append('Invalid combination of username and password')
        return False

class SystemEditForm(FlaskForm):
    #todo limit field lengths?
    system_name_edit = HiddenField()
    system_name = StringField("System name*", validators=[DataRequired()], render_kw={'autofocus': True})
    system_description = TextAreaField("System description")
    submit = SubmitField("Save")

    def validate(self, extra_validators=None):
        valid = super(SystemEditForm, self).validate(extra_validators)
        if not valid:
            return False

        #todo check
        if self.system_name.data != self.system_name_edit.data:
            try:
                SystemUnique(self, self.system_name)
            except ValidationError as e:
                self.system_name.errors.append(e)
                return False

        return True

class DeviceEditForm(FlaskForm):
    device_name = StringField("Name*", validators = [DataRequired()], render_kw={'autofocus': True})
    device_description = TextAreaField("Description")
    device_type = SelectField("Type*", validators=[DataRequired()], coerce=int)
    submit = SubmitField("Save")
    
class DeviceTypeEditForm(FlaskForm):
    device_type_name = StringField("Name*", validators = [DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField("Save")

class ParameterEditForm(FlaskForm):
    parameter_name = StringField("Name*", validators = [DataRequired()], render_kw={'autofocus': True})
    parameter_unit = StringField("Unit*", validators = [DataRequired()])
    submit = SubmitField("Save")

class UserEditForm(FlaskForm):
    username_edit = HiddenField()
    username = StringField("Username*", validators=[DataRequired()], render_kw={'autofocus': True})
    first_name = StringField("First name*", validators=[DataRequired()])
    last_name = StringField("Last name*", validators=[DataRequired()])
    submit = SubmitField("Save")

    def validate(self, extra_validators=None):
        valid = super(UserEditForm, self).validate(extra_validators)
        if not valid:
            return False

        #todo check
        if self.username.data != self.username_edit.data:
            try:
                UsernameUnique(self, self.username)
            except ValidationError as e:
                self.system_name.errors.append(e)
                return False

        return True

class PasswordEdit(FlaskForm):
    password = PasswordField("Password*", validators=[DataRequired()])
    passwordConfirm = PasswordField("Confirm password*", validators=[DataRequired()])
    submit = SubmitField("Save")

    def validate(self, extra_validators=None):
        valid = super(PasswordEdit, self).validate(extra_validators)
        if not valid:
            return False

        if self.password.data == self.passwordConfirm.data:
            return True

        self.passwordConfirm.errors.append('Passwords do not match.')
        return False
