from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, EqualTo


class ProfileForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Teléfono", validators=[Optional(), Length(max=30)])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Contraseña actual", validators=[DataRequired()])
    new_password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("new_password")])


class AddressForm(FlaskForm):
    label = StringField("Etiqueta", validators=[DataRequired(), Length(max=50)])
    recipient_name = StringField("Nombre de quien recibe", validators=[Optional(), Length(max=150)])
    line1 = StringField("Dirección", validators=[DataRequired(), Length(max=255)])
    line2 = StringField("Detalle adicional", validators=[Optional(), Length(max=255)])
    city = StringField("Ciudad", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Teléfono de contacto", validators=[Optional(), Length(max=30)])
    notes = StringField("Notas de entrega", validators=[Optional(), Length(max=255)])
    is_default = BooleanField("Usar como dirección principal")
