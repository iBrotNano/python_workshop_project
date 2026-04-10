from dataclasses import dataclass, field


@dataclass
class Nutrition:
    """
    Represents a normalized nutrition record.

    :param id: The unique database identifier of the nutrition record.
    :type id: int | None
    :param code: The external product or source code.
    :type code: str | None
    :param name: The display name of the nutrition record.
    :type name: str
    :param brands: The brands associated with the product.
    :type brands: list[str]
    :param synonyms: Alternative names for the product.
    :type synonyms: list[str]
    :param categories: Categories assigned to the product.
    :type categories: list[str]
    :param quantity: The quantity label of the product.
    :type quantity: str | None
    :param energy_100g_kj: Energy in kilojoules per 100 g.
    :type energy_100g_kj: float | None
    :param fat_100g: Total fat per 100 g.
    :type fat_100g: float | None
    :param saturated_fat_100g: Saturated fat per 100 g.
    :type saturated_fat_100g: float | None
    :param butyric_acid_100g: Butyric acid per 100 g.
    :type butyric_acid_100g: float | None
    :param caproic_acid_100g: Caproic acid per 100 g.
    :type caproic_acid_100g: float | None
    :param caprylic_acid_100g: Caprylic acid per 100 g.
    :type caprylic_acid_100g: float | None
    :param capric_acid_100g: Capric acid per 100 g.
    :type capric_acid_100g: float | None
    :param lauric_acid_100g: Lauric acid per 100 g.
    :type lauric_acid_100g: float | None
    :param myristic_acid_100g: Myristic acid per 100 g.
    :type myristic_acid_100g: float | None
    :param palmitic_acid_100g: Palmitic acid per 100 g.
    :type palmitic_acid_100g: float | None
    :param stearic_acid_100g: Stearic acid per 100 g.
    :type stearic_acid_100g: float | None
    :param arachidic_acid_100g: Arachidic acid per 100 g.
    :type arachidic_acid_100g: float | None
    :param behenic_acid_100g: Behenic acid per 100 g.
    :type behenic_acid_100g: float | None
    :param lignoceric_acid_100g: Lignoceric acid per 100 g.
    :type lignoceric_acid_100g: float | None
    :param cerotic_acid_100g: Cerotic acid per 100 g.
    :type cerotic_acid_100g: float | None
    :param montanic_acid_100g: Montanic acid per 100 g.
    :type montanic_acid_100g: float | None
    :param melissic_acid_100g: Melissic acid per 100 g.
    :type melissic_acid_100g: float | None
    :param monounsaturated_fat_100g: Monounsaturated fat per 100 g.
    :type monounsaturated_fat_100g: float | None
    :param polyunsaturated_fat_100g: Polyunsaturated fat per 100 g.
    :type polyunsaturated_fat_100g: float | None
    :param alpha_linolenic_acid_100g: Alpha-linolenic acid per 100 g.
    :type alpha_linolenic_acid_100g: float | None
    :param eicosapentaenoic_acid_100g: Eicosapentaenoic acid per 100 g.
    :type eicosapentaenoic_acid_100g: float | None
    :param docosahexaenoic_acid_100g: Docosahexaenoic acid per 100 g.
    :type docosahexaenoic_acid_100g: float | None
    :param linoleic_acid_100g: Linoleic acid per 100 g.
    :type linoleic_acid_100g: float | None
    :param arachidonic_acid_100g: Arachidonic acid per 100 g.
    :type arachidonic_acid_100g: float | None
    :param gamma_linolenic_acid_100g: Gamma-linolenic acid per 100 g.
    :type gamma_linolenic_acid_100g: float | None
    :param dihomo_gamma_linolenic_acid_100g: Dihomo-gamma-linolenic acid per 100 g.
    :type dihomo_gamma_linolenic_acid_100g: float | None
    :param oleic_acid_100g: Oleic acid per 100 g.
    :type oleic_acid_100g: float | None
    :param elaidic_acid_100g: Elaidic acid per 100 g.
    :type elaidic_acid_100g: float | None
    :param gondoic_acid_100g: Gondoic acid per 100 g.
    :type gondoic_acid_100g: float | None
    :param mead_acid_100g: Mead acid per 100 g.
    :type mead_acid_100g: float | None
    :param erucic_acid_100g: Erucic acid per 100 g.
    :type erucic_acid_100g: float | None
    :param nervonic_acid_100g: Nervonic acid per 100 g.
    :type nervonic_acid_100g: float | None
    :param trans_fat_100g: Trans fat per 100 g.
    :type trans_fat_100g: float | None
    :param cholesterol_100g: Cholesterol per 100 g.
    :type cholesterol_100g: float | None
    :param carbohydrates_100g: Carbohydrates per 100 g.
    :type carbohydrates_100g: float | None
    :param sugars_100g: Sugars per 100 g.
    :type sugars_100g: float | None
    :param sucrose_100g: Sucrose per 100 g.
    :type sucrose_100g: float | None
    :param glucose_100g: Glucose per 100 g.
    :type glucose_100g: float | None
    :param fructose_100g: Fructose per 100 g.
    :type fructose_100g: float | None
    :param galactose_100g: Galactose per 100 g.
    :type galactose_100g: float | None
    :param lactose_100g: Lactose per 100 g.
    :type lactose_100g: float | None
    :param maltose_100g: Maltose per 100 g.
    :type maltose_100g: float | None
    :param maltodextrins_100g: Maltodextrins per 100 g.
    :type maltodextrins_100g: float | None
    :param starch_100g: Starch per 100 g.
    :type starch_100g: float | None
    :param fiber_100g: Fiber per 100 g.
    :type fiber_100g: float | None
    :param proteins_100g: Proteins per 100 g.
    :type proteins_100g: float | None
    :param salt_100g: Salt per 100 g.
    :type salt_100g: float | None
    :param alcohol_100g: Alcohol per 100 g.
    :type alcohol_100g: float | None
    :param vitamin_a_100g: Vitamin A per 100 g.
    :type vitamin_a_100g: float | None
    :param beta_carotene_100g: Beta-carotene per 100 g.
    :type beta_carotene_100g: float | None
    :param vitamin_b1_100g: Vitamin B1 per 100 g.
    :type vitamin_b1_100g: float | None
    :param vitamin_b2_100g: Vitamin B2 per 100 g.
    :type vitamin_b2_100g: float | None
    :param vitamin_b3_100g: Vitamin B3 per 100 g.
    :type vitamin_b3_100g: float | None
    :param vitamin_b6_100g: Vitamin B6 per 100 g.
    :type vitamin_b6_100g: float | None
    :param vitamin_b9_100g: Vitamin B9 per 100 g.
    :type vitamin_b9_100g: float | None
    :param vitamin_b12_100g: Vitamin B12 per 100 g.
    :type vitamin_b12_100g: float | None
    :param pantothenic_acid_100g: Pantothenic acid per 100 g.
    :type pantothenic_acid_100g: float | None
    :param vitamin_c_100g: Vitamin C per 100 g.
    :type vitamin_c_100g: float | None
    :param vitamin_d_100g: Vitamin D per 100 g.
    :type vitamin_d_100g: float | None
    :param vitamin_e_100g: Vitamin E per 100 g.
    :type vitamin_e_100g: float | None
    :param vitamin_k_100g: Vitamin K per 100 g.
    :type vitamin_k_100g: float | None
    :param potassium_100g: Potassium per 100 g.
    :type potassium_100g: float | None
    :param sodium_100g: Sodium per 100 g.
    :type sodium_100g: float | None
    :param chloride_100g: Chloride per 100 g.
    :type chloride_100g: float | None
    :param calcium_100g: Calcium per 100 g.
    :type calcium_100g: float | None
    :param magnesium_100g: Magnesium per 100 g.
    :type magnesium_100g: float | None
    :param phosphorus_100g: Phosphorus per 100 g.
    :type phosphorus_100g: float | None
    :param iron_100g: Iron per 100 g.
    :type iron_100g: float | None
    :param iodine_100g: Iodine per 100 g.
    :type iodine_100g: float | None
    :param zinc_100g: Zinc per 100 g.
    :type zinc_100g: float | None
    :param selenium_100g: Selenium per 100 g.
    :type selenium_100g: float | None
    :param folates_100g: Folates per 100 g.
    :type folates_100g: float | None
    :param biotin_100g: Biotin per 100 g.
    :type biotin_100g: float | None
    :param silica_100g: Silica per 100 g.
    :type silica_100g: float | None
    :param bicarbonate_100g: Bicarbonate per 100 g.
    :type bicarbonate_100g: float | None
    :param copper_100g: Copper per 100 g.
    :type copper_100g: float | None
    :param manganese_100g: Manganese per 100 g.
    :type manganese_100g: float | None
    :param fluoride_100g: Fluoride per 100 g.
    :type fluoride_100g: float | None
    :param chromium_100g: Chromium per 100 g.
    :type chromium_100g: float | None
    :param molybdenum_100g: Molybdenum per 100 g.
    :type molybdenum_100g: float | None
    """

    id: int = 0
    code: str | None = None
    name: str | None = None
    url: str | None = None
    brands: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    quantity: str | None = None
    energy_100g_kj: float | None = None
    fat_100g: float | None = None
    saturated_fat_100g: float | None = None
    butyric_acid_100g: float | None = None
    caproic_acid_100g: float | None = None
    caprylic_acid_100g: float | None = None
    capric_acid_100g: float | None = None
    lauric_acid_100g: float | None = None
    myristic_acid_100g: float | None = None
    palmitic_acid_100g: float | None = None
    stearic_acid_100g: float | None = None
    arachidic_acid_100g: float | None = None
    behenic_acid_100g: float | None = None
    lignoceric_acid_100g: float | None = None
    cerotic_acid_100g: float | None = None
    montanic_acid_100g: float | None = None
    melissic_acid_100g: float | None = None
    monounsaturated_fat_100g: float | None = None
    polyunsaturated_fat_100g: float | None = None
    alpha_linolenic_acid_100g: float | None = None
    eicosapentaenoic_acid_100g: float | None = None
    docosahexaenoic_acid_100g: float | None = None
    linoleic_acid_100g: float | None = None
    arachidonic_acid_100g: float | None = None
    gamma_linolenic_acid_100g: float | None = None
    dihomo_gamma_linolenic_acid_100g: float | None = None
    oleic_acid_100g: float | None = None
    elaidic_acid_100g: float | None = None
    gondoic_acid_100g: float | None = None
    mead_acid_100g: float | None = None
    erucic_acid_100g: float | None = None
    nervonic_acid_100g: float | None = None
    trans_fat_100g: float | None = None
    cholesterol_100g: float | None = None
    carbohydrates_100g: float | None = None
    sugars_100g: float | None = None
    sucrose_100g: float | None = None
    glucose_100g: float | None = None
    fructose_100g: float | None = None
    galactose_100g: float | None = None
    lactose_100g: float | None = None
    maltose_100g: float | None = None
    maltodextrins_100g: float | None = None
    starch_100g: float | None = None
    fiber_100g: float | None = None
    proteins_100g: float | None = None
    salt_100g: float | None = None
    alcohol_100g: float | None = None
    vitamin_a_100g: float | None = None
    beta_carotene_100g: float | None = None
    vitamin_b1_100g: float | None = None
    vitamin_b2_100g: float | None = None
    vitamin_b3_100g: float | None = None
    vitamin_b6_100g: float | None = None
    vitamin_b9_100g: float | None = None
    vitamin_b12_100g: float | None = None
    pantothenic_acid_100g: float | None = None
    vitamin_c_100g: float | None = None
    vitamin_d_100g: float | None = None
    vitamin_e_100g: float | None = None
    vitamin_k_100g: float | None = None
    potassium_100g: float | None = None
    sodium_100g: float | None = None
    chloride_100g: float | None = None
    calcium_100g: float | None = None
    magnesium_100g: float | None = None
    phosphorus_100g: float | None = None
    iron_100g: float | None = None
    iodine_100g: float | None = None
    zinc_100g: float | None = None
    selenium_100g: float | None = None
    folates_100g: float | None = None
    biotin_100g: float | None = None
    silica_100g: float | None = None
    bicarbonate_100g: float | None = None
    copper_100g: float | None = None
    manganese_100g: float | None = None
    fluoride_100g: float | None = None
    chromium_100g: float | None = None
    molybdenum_100g: float | None = None
