import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Couleurs La Certitude
NAVY  = colors.HexColor('#0b1c3d')
GOLD  = colors.HexColor('#c9922a')
CREAM = colors.HexColor('#fdf6ec')
WHITE = colors.white
GREY  = colors.HexColor('#6b7280')
GREEN = colors.HexColor('#2a7f6f')


def generate_receipt_pdf(enrollment, payments):
    """
    Génère un reçu PDF professionnel pour une inscription.
    Retourne un buffer io.BytesIO.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Style personnalisés ─────────────────────────────
    title_style = ParagraphStyle(
        'Title', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=2,
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        textColor=NAVY, spaceAfter=6, spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'Normal2', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        textColor=NAVY, spaceAfter=3,
    )
    center_style = ParagraphStyle(
        'Center', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        textColor=GREY, alignment=TA_CENTER,
    )

    # ── EN-TÊTE ─────────────────────────────────────────
    # Bande bleue titre
    header_data = [[
        Paragraph('<font color="white"><b>GROUPE LA CERTITUDE</b></font>', ParagraphStyle(
            'H', fontName='Helvetica-Bold', fontSize=18,
            textColor=WHITE, alignment=TA_CENTER,
        )),
    ]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('PADDING',    (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # Sous-titre
    story.append(Paragraph('Discipline · Travail · Excellence', subtitle_style))
    story.append(Paragraph('EPP Gbégamey Sud, Cotonou — Bénin | Tél : 01 96 38 92 49', subtitle_style))
    story.append(Spacer(1, 0.5*cm))

    # Ligne dorée
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD, spaceAfter=12))

    # Titre REÇU
    story.append(Paragraph('REÇU DE PAIEMENT', title_style))
    story.append(Paragraph('Cours Intensifs de Renforcement — Juillet–Août 2026', subtitle_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=12))

    # ── INFOS APPRENANT ─────────────────────────────────
    story.append(Paragraph('👤  INFORMATIONS DE L\'APPRENANT', section_style))

    student = enrollment.student
    apprenant_data = [
        ['Nom complet',       student.full_name],
        ['Nom d\'utilisateur', student.username],
        ['Téléphone',          student.phone or '—'],
        ['Établissement',      student.school or '—'],
        ['Classe / Niveau',    student.get_level_display() if student.level else '—'],
    ]
    apprenant_table = Table(apprenant_data, colWidths=[5*cm, 12*cm])
    apprenant_table.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('TEXTCOLOR',   (0,0), (0,-1), GREY),
        ('TEXTCOLOR',   (1,0), (1,-1), NAVY),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CREAM, WHITE]),
        ('PADDING',     (0,0), (-1,-1), 7),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(apprenant_table)
    story.append(Spacer(1, 0.4*cm))

    # ── FORMATION ───────────────────────────────────────
    story.append(Paragraph('📚  FORMATION INSCRITE', section_style))

    course = enrollment.course
    course_data = [
        ['Formation',     course.title],
        ['Niveau',        course.get_level_display()],
        ['Matières',      course.subjects],
        ['Période',       f"{course.start_date.strftime('%d/%m/%Y')} → {course.end_date.strftime('%d/%m/%Y')}"],
        ['Prix total',    f"{int(course.price):,} FCFA".replace(',', ' ')],
        ['Statut',        '✓ Active' if enrollment.status == 'active' else '⏳ En attente'],
    ]
    course_table = Table(course_data, colWidths=[5*cm, 12*cm])
    course_table.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('TEXTCOLOR',   (0,0), (0,-1), GREY),
        ('TEXTCOLOR',   (1,0), (1,-1), NAVY),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CREAM, WHITE]),
        ('PADDING',     (0,0), (-1,-1), 7),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(course_table)
    story.append(Spacer(1, 0.4*cm))

    # ── PAIEMENTS ───────────────────────────────────────
    story.append(Paragraph('💳  DÉTAIL DES PAIEMENTS', section_style))

    pay_header = [['#', 'Date', 'Méthode', 'Référence', 'Montant', 'Statut']]
    pay_rows = []

    payment_list = list(payments) if hasattr(payments, '__iter__') else [payments]
    total_confirmed = 0

    for i, p in enumerate(payment_list, 1):
        date_str = p.paid_at.strftime('%d/%m/%Y %H:%M') if p.paid_at else p.created_at.strftime('%d/%m/%Y')
        montant  = f"{int(p.amount):,} FCFA".replace(',', ' ')
        statut   = '✓ Confirmé' if p.status == 'confirmed' else '⏳ En attente'
        ref      = p.reference[:12] + '...' if len(p.reference) > 12 else p.reference or '—'
        pay_rows.append([str(i), date_str, p.get_method_display(), ref, montant, statut])
        if p.status == 'confirmed':
            total_confirmed += int(p.amount)

    pay_data = pay_header + pay_rows
    pay_table = Table(pay_data, colWidths=[0.7*cm, 3.5*cm, 3*cm, 3.5*cm, 3*cm, 3.3*cm])
    pay_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CREAM, WHITE]),
        ('TEXTCOLOR',   (0,1), (-1,-1), NAVY),
        ('PADDING',     (0,0), (-1,-1), 6),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('ALIGN',       (4,0), (4,-1), 'RIGHT'),
    ]))
    story.append(pay_table)
    story.append(Spacer(1, 0.3*cm))

    # Résumé financier
    reste = int(course.price) - total_confirmed
    summary_data = [
        ['Total payé',    f"{total_confirmed:,} FCFA".replace(',', ' ')],
        ['Reste à payer', f"{max(reste, 0):,} FCFA".replace(',', ' ')],
        ['Prix total',    f"{int(course.price):,} FCFA".replace(',', ' ')],
    ]
    summary_table = Table(summary_data, colWidths=[10*cm, 7*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (1,0), (1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 10),
        ('TEXTCOLOR',  (0,0), (0,-1), GREY),
        ('TEXTCOLOR',  (1,0), (1,-1), NAVY),
        ('ALIGN',      (1,0), (1,-1), 'RIGHT'),
        ('LINEABOVE',  (0,-1), (-1,-1), 1.5, GOLD),
        ('PADDING',    (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.6*cm))

    # ── PIED DE PAGE ────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=10))

    footer_data = [[
        Paragraph(
            f'<font color="{GREY.hexval()}">Reçu généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}</font>',
            ParagraphStyle('F', fontName='Helvetica', fontSize=8, textColor=GREY, alignment=TA_LEFT)
        ),
        Paragraph(
            '<font color="#c9922a"><b>Groupe La Certitude © 2026</b></font>',
            ParagraphStyle('F2', fontName='Helvetica-Bold', fontSize=8, textColor=GOLD, alignment=TA_RIGHT)
        ),
    ]]
    footer_table = Table(footer_data, colWidths=[8.5*cm, 8.5*cm])
    footer_table.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 0)]))
    story.append(footer_table)

    # Note importante
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '⚠ Ce reçu est un document officiel émis par le Groupe La Certitude. '
        'Conservez-le précieusement. Pour toute question, contactez-nous au 01 96 38 92 49.',
        ParagraphStyle('Note', fontName='Helvetica-Oblique', fontSize=7.5,
                       textColor=GREY, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer