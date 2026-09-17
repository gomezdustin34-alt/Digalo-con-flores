from datetime import datetime, timezone

from flask import render_template, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import CampaignForm
from app.extensions import db
from app.models.campaign import EmailCampaign
from app.models.subscriber import Subscriber
from app.services.email import get_email_provider


@bp.route("/campanas")
def campaigns_list():
    campaigns = EmailCampaign.query.order_by(EmailCampaign.created_at.desc()).all()
    active_subscribers = Subscriber.query.filter_by(is_active=True).count()
    return render_template("admin/campaigns/list.html", campaigns=campaigns, active_subscribers=active_subscribers)


@bp.route("/campanas/nueva", methods=["GET", "POST"])
def campaign_new():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign = EmailCampaign()
        form.populate_obj(campaign)
        campaign.status = "programada" if campaign.scheduled_at else "borrador"
        db.session.add(campaign)
        db.session.commit()
        flash("Campaña guardada.", "success")
        return redirect(url_for("admin.campaigns_list"))
    return render_template("admin/campaigns/form.html", form=form, campaign=None)


@bp.route("/campanas/<int:campaign_id>/editar", methods=["GET", "POST"])
def campaign_edit(campaign_id):
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    if campaign.status == "enviada":
        flash("Esta campaña ya fue enviada y no se puede editar.", "danger")
        return redirect(url_for("admin.campaigns_list"))

    form = CampaignForm(obj=campaign)
    if form.validate_on_submit():
        form.populate_obj(campaign)
        campaign.status = "programada" if campaign.scheduled_at else "borrador"
        db.session.commit()
        flash("Campaña actualizada.", "success")
        return redirect(url_for("admin.campaigns_list"))
    return render_template("admin/campaigns/form.html", form=form, campaign=campaign)


@bp.route("/campanas/<int:campaign_id>/eliminar", methods=["POST"])
def campaign_delete(campaign_id):
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaña eliminada.", "info")
    return redirect(url_for("admin.campaigns_list"))


@bp.route("/campanas/<int:campaign_id>/enviar", methods=["POST"])
def campaign_send(campaign_id):
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    if campaign.status == "enviada":
        # Un doble clic o un reenvio del formulario la mandaba otra vez a todos.
        flash("Esta campaña ya fue enviada.", "info")
        return redirect(url_for("admin.campaigns_list"))
    recipients = [s.email for s in Subscriber.query.filter_by(is_active=True).all()]

    sent = get_email_provider().send_bulk(recipients, campaign.subject, campaign.content_html)

    campaign.status = "enviada"
    campaign.sent_at = datetime.now(timezone.utc)
    campaign.recipients_count = sent
    db.session.commit()

    flash(f"Campaña enviada a {sent} suscriptores.", "success")
    return redirect(url_for("admin.campaigns_list"))
