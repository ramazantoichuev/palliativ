from resources.models.resources import Resource

ALL_AUDIENCES = [
    Resource.AUDIENCE_SPECIALIST,
    Resource.AUDIENCE_CAREGIVER,
    Resource.AUDIENCE_PEDIATRIC,
]


def allowed_audiences(*, for_doctor, is_child):
    """Врач: specialist + (pediatric | caregiver). Пациент: только свой."""
    own = Resource.AUDIENCE_PEDIATRIC if is_child else Resource.AUDIENCE_CAREGIVER
    if for_doctor:
        return [Resource.AUDIENCE_SPECIALIST, own]
    return [own]


def fetch_resources(symptom_ids, audiences):
    return list(
        Resource.objects.filter(
            symptoms__id__in=symptom_ids, audience__in=audiences
        )
        .distinct()
        .order_by("-created_at")
        .prefetch_related("symptoms")
    )


def group_resources(symptoms, resources, audiences):
    """[{"symptom": s, "resources": [...]}, ...]. Материал виден в группе
    каждого подходящего симптома карточки."""
    by_symptom = {s.id: [] for s in symptoms}
    for resource in resources:
        if resource.audience not in audiences:
            continue
        for symptom in resource.symptoms.all():
            if symptom.id in by_symptom:
                by_symptom[symptom.id].append(resource)
    return [{"symptom": s, "resources": by_symptom[s.id]} for s in symptoms]


def match_resources(symptoms, *, for_doctor, is_child):
    symptoms = list(symptoms)
    if not symptoms:
        return []
    audiences = allowed_audiences(for_doctor=for_doctor, is_child=is_child)
    resources = fetch_resources([s.id for s in symptoms], audiences)
    return group_resources(symptoms, resources, audiences)


def match_for_cards(cards):
    """Кабинет врача: один запрос материалов на все карточки.
    Результат кладётся в card._resource_groups."""
    ids = {s.id for card in cards for s in card.symptoms.all()}
    resources = fetch_resources(ids, ALL_AUDIENCES) if ids else []
    for card in cards:
        audiences = allowed_audiences(
            for_doctor=True, is_child=card.patient.is_child
        )
        card._resource_groups = group_resources(
            list(card.symptoms.all()), resources, audiences
        )
    return cards
