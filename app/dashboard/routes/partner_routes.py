from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from werkzeug.datastructures import FileStorage

from app.dashboard import bp
from app.extensions import db
from app.models import Partner
from app.forms import PartnerForm
from app.utils import save_picture, delete_file_from_uploads


@bp.route('/partners')
@login_required
def list_partners():
    partners = Partner.query.order_by(Partner.name).all()
    return render_template('dashboard/partners.html', partners=partners, title='Parceiros')


@bp.route('/partners/new', methods=['GET', 'POST'])
@login_required
def add_partner():
    form = PartnerForm()
    if form.validate_on_submit():
        partner = Partner(
            name=form.name.data,
            phone=form.phone.data,
            instagram=form.instagram.data,
            email=form.email.data,
            is_active=form.is_active.data
        )
        if isinstance(form.logo.data, FileStorage):
            logo_filename = save_picture(form.logo.data)
            partner.logo_filename = None if logo_filename == 'default.jpg' else logo_filename

        db.session.add(partner)
        db.session.commit()
        flash('Parceiro cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard.list_partners'))
    return render_template('dashboard/manage_partner.html', form=form, title='Novo Parceiro')


@bp.route('/partners/edit/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def edit_partner(partner_id):
    partner = Partner.query.get_or_404(partner_id)
    form = PartnerForm(obj=partner)
    if form.validate_on_submit():
        form.populate_obj(partner)

        if isinstance(form.logo.data, FileStorage):
            delete_file_from_uploads(partner.logo_filename)
            logo_filename = save_picture(form.logo.data)
            partner.logo_filename = None if logo_filename == 'default.jpg' else logo_filename
        elif form.remove_logo.data:
            delete_file_from_uploads(partner.logo_filename)
            partner.logo_filename = None

        db.session.commit()
        flash('Parceiro atualizado com sucesso!', 'success')
        return redirect(url_for('dashboard.list_partners'))

    return render_template('dashboard/manage_partner.html', form=form, title='Editar Parceiro', partner=partner)


@bp.route('/partners/delete/<int:partner_id>', methods=['POST'])
@login_required
def delete_partner(partner_id):
    partner = Partner.query.get_or_404(partner_id)
    delete_file_from_uploads(partner.logo_filename)
    db.session.delete(partner)
    db.session.commit()
    flash('Parceiro removido com sucesso!', 'success')
    return redirect(url_for('dashboard.list_partners'))
