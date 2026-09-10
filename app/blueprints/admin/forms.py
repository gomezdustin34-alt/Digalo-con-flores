from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, DecimalField, IntegerField, BooleanField,
    SelectField, DateField, DateTimeField,
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class ProductForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=200)])
    short_description = StringField("Descripción corta", validators=[Optional(), Length(max=300)])
    description = TextAreaField("Descripción", validators=[Optional()])

    price = DecimalField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    compare_at_price = DecimalField("Precio anterior", validators=[Optional(), NumberRange(min=0)])

    sku = StringField("SKU", validators=[Optional(), Length(max=60)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    stock_minimo = IntegerField("Stock mínimo", validators=[Optional(), NumberRange(min=0)])

    category_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])

    is_active = BooleanField("Publicado", default=True)
    is_featured = BooleanField("Destacado")
    is_new = BooleanField("Nuevo")
    tags = StringField("Etiquetas (separadas por coma)", validators=[Optional(), Length(max=300)])

    allow_dedication = BooleanField("Permitir dedicatoria", default=True)
    allow_recipient_name = BooleanField("Permitir nombre del destinatario", default=True)
    allow_delivery_datetime = BooleanField("Permitir elegir fecha/hora de entrega", default=True)
    allow_color_choice = BooleanField("Permitir elegir color")
    allow_size_choice = BooleanField("Permitir elegir tamaño")

    image = FileField("Imagen principal", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes.")])


class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Descripción", validators=[Optional()])
    icon = StringField("Ícono (emoji)", validators=[Optional(), Length(max=10)])
    sort_order = IntegerField("Orden", validators=[Optional()], default=0)
    is_active = BooleanField("Activa", default=True)
    image = FileField("Imagen", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes.")])


class CouponForm(FlaskForm):
    code = StringField("Código", validators=[DataRequired(), Length(max=40)])
    discount_type = SelectField("Tipo de descuento", choices=[("percent", "Porcentaje"), ("fixed", "Monto fijo")])
    discount_value = DecimalField("Valor del descuento", validators=[DataRequired(), NumberRange(min=0)])
    starts_at = DateField("Fecha de inicio", validators=[Optional()])
    expires_at = DateField("Fecha de expiración", validators=[Optional()])
    max_uses = IntegerField("Usos máximos", validators=[Optional(), NumberRange(min=1)])
    min_purchase = DecimalField("Compra mínima", validators=[Optional(), NumberRange(min=0)], default=0)
    is_active = BooleanField("Activo", default=True)


class TestimonialForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=150)])
    comment = TextAreaField("Comentario", validators=[DataRequired()])
    rating = IntegerField("Calificación (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    status = SelectField("Estado", choices=[("pendiente", "Pendiente"), ("aprobado", "Aprobado"), ("oculto", "Oculto")])
    photo = FileField("Foto", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes.")])


class CampaignForm(FlaskForm):
    subject = StringField("Asunto", validators=[DataRequired(), Length(max=200)])
    content_html = TextAreaField("Contenido (HTML)", validators=[DataRequired()])
    scheduled_at = DateTimeField("Programar envío (opcional)", validators=[Optional()], format="%Y-%m-%dT%H:%M")


class StaffUserForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    role = SelectField("Rol", choices=[
        ("super_admin", "Super administrador"),
        ("admin", "Administrador"),
        ("editor", "Editor"),
        ("order_manager", "Gestor de pedidos"),
    ])
    password = StringField("Contraseña (dejar en blanco para no cambiar)", validators=[Optional(), Length(min=8)])
