# ChatbotDuolingo_FSM_v3.py
# -*- coding: utf-8 -*-
import re
import unicodedata

# ---- Config ----
SHOW_DEBUG = False # pon True para ver qué patrón/estado se activó

def dbg(msg: str):
    if SHOW_DEBUG:
        print(f"[DEBUG] {msg}")

def normaliza(txt: str) -> str:
    txt = (txt or "").strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    return txt.lower()

# ---- patrones base ----
salir_RE = re.compile(r"^(no|salir|me equivoque|perdon|adios|deseo (salir|interrumpir))$", re.IGNORECASE)

# saludos / ayuda general / opciones
hola_RE = re.compile(r"^(hola|buenas|hey|que tal|ayuda( por favor)?|menu|opciones)$", re.IGNORECASE)

# --- Patrones con raíces/sinónimos reforzados ---
# 1 ¿Quién creó Duolingo?
q1_RE  = re.compile(r"(quien|quienes|creador(es)?|fundador(es)?|fundo|creo).*duolingo", re.IGNORECASE)

# 2 ¿Dónde ayuda oficial?
q2_RE  = re.compile(r"(donde|donde puedo|ayuda|soporte|asistencia).*(duolingo|oficial|centro|wiki|comunidad)", re.IGNORECASE)

# 3 Modelo de negocio
q3_RE  = re.compile(r"(modelo|como gana|ingresos?|negocio).*(duolingo)", re.IGNORECASE)

# 4 Frecuencia de actualizaciones
q4_RE  = re.compile(r"(cada cuan|frecuen|cuando).*(actualiz|updates?)", re.IGNORECASE)

# 5 Por qué no tienen X función
q5_RE  = re.compile(r"(por ?que|porque).*(no (tiene|hay)).*(funcion|feature|opcional)", re.IGNORECASE)

# 6 Pruebas A/B
q6_RE  = re.compile(r"(tengo.*funcion.*(amigos?|otros)|mis amigos?.*no (tienen|ven)|pruebas? ?a/?b|experiment(os|ales)?)", re.IGNORECASE)

# 7 Tenía una función y ya no
q7_RE  = re.compile(r"(teni(a|amos|an)).*funcion.*(ya no|desaparec|quit|retir|paus)", re.IGNORECASE)

# 8 ¿Por qué cambió mi curso?
q8_RE  = re.compile(r"(por ?que|porque).*(cambi(o|o)).*curso|mi curso cambi(o|o)", re.IGNORECASE)

# 9 ¿Cuántos idiomas ofrece?
q9_RE  = re.compile(r"(cuant[oa]s?).*(idiomas?|lenguajes?).*(ofrece|hay|disponibles?)", re.IGNORECASE)

# 10 ¿Cuántos idiomas a la vez?
q10_RE = re.compile(r"(cuant[oa]s?).*(idiomas?|lenguajes?).*(a la vez|simultan|paralel)|estudiar.*varios", re.IGNORECASE)

# 11 Idiomas inventados
q11_RE = re.compile(r"(idiomas?|lenguas?).*(inventad|construid|fictici|cread|artificial)", re.IGNORECASE)

# 12 Lenguas en peligro
q12_RE = re.compile(r"(lenguas?|idiomas?).*(en peligro|amenazad|revitaliz)", re.IGNORECASE)

# 13 Idiomas africanos
q13_RE = re.compile(r"(idiomas?|lenguajes?).*(african|africa)|\bsuajili\b|\bzulu\b|zul[uú]|\bxhosa\b", re.IGNORECASE)

# 14 Qué idioma aprender
q14_RE = re.compile(r"(que|cual).*(idioma).*(deberia|me conviene|recomiend|elegir)", re.IGNORECASE)

# 15 Empezar otro curso
q15_RE = re.compile(r"(como|c[oó]mo).*(empez|agreg|inici).*(otro|nuevo).*curso", re.IGNORECASE)

# 16 Cambiar de idioma/curso
q16_RE = re.compile(r"(cambi|switch|altern).*(idioma|curso)", re.IGNORECASE)

# 17 Reiniciar curso
q17_RE = re.compile(r"(reinici|empezar de cero|reset).*curso", re.IGNORECASE)

# 18 Eliminar un idioma
q18_RE = re.compile(r"(elimin|borr|quit).*(idioma|curso)", re.IGNORECASE)

# 19 Racha
q19_RE = re.compile(r"(que|que es|como funciona).*(racha|streak)", re.IGNORECASE)

# 20 Ligas/divisiones
q20_RE = re.compile(r"(ligas?|divisiones?|clasificac|liga semanal)", re.IGNORECASE)

# 21 Stories
q21_RE = re.compile(r"(stories|historias).*(que cursos|cuales idiomas|disponibles?)", re.IGNORECASE)

# 22 Podcasts
q22_RE = re.compile(r"(podcasts?).*(idiomas?|cuales?)", re.IGNORECASE)

# 23 Buscar/seguir/bloquear usuarios (incluye “alguien/persona”)
q23_RE = re.compile(r"(busc|segu(i|ir)|dejar de segu|bloque|report).*(usuarios?|amigos?|personas?|alguien)", re.IGNORECASE)

# 24 Dónde ver amigos
q24_RE = re.compile(r"(donde|d[oó]nde).*(veo|ver).*(amigos?|lista de amigos)", re.IGNORECASE)

# 25 No puedo seguir a alguien
q25_RE = re.compile(r"(no puedo|no me deja|problema).*(segu(i|ir)).*(alguien|usuario|amigo)", re.IGNORECASE)

# 26 Enviar felicitaciones
q26_RE = re.compile(r"(envi|mand).*(felicit|congrats|mensaje de apoyo)", re.IGNORECASE)

# 27 Hacer perfil/cuenta privada
q27_RE = re.compile(r"(hac|pon|volv|dej).*privad[oa]s?.*(perfil|cuenta)", re.IGNORECASE)

# 28 Cambiar usuario/correo
q28_RE = re.compile(r"(cambi|edit|actualiz).*(nombre de usuario|usuario|correo|email)", re.IGNORECASE)

# 29 Problemas para acceder
q29_RE = re.compile(r"(no puedo|problem|error).*(acced|iniciar sesi[oó]n|entrar|login|cuenta)", re.IGNORECASE)

# 30 Eliminar cuenta/datos (raíces y conjugaciones)
q30_RE = re.compile(r"(elimin(ar|o|a|e|aste|aron|ado|ando)?|borr(ar|o|a|e|aste|aron|ado|ando)?|quit(ar|o|a|e)).*(cuenta|datos?|informaci[oó]n)", re.IGNORECASE)

# 31 Datos comprometidos
q31_RE = re.compile(r"(datos?|seguridad).*(comprometid|filtraci[oó]n|brecha|hack)", re.IGNORECASE)

# 32 Súper Duolingo (beneficios)
q32_RE = re.compile(r"(que es|beneficios?).*(super duolingo|super\b)", re.IGNORECASE)

# 33 Plan Familiar
q33_RE = re.compile(r"(plan|familiar).*(super\b|super duolingo)", re.IGNORECASE)

# 34 Duolingo Max
q34_RE = re.compile(r"(que es|info|informaci[oó]n).*(duolingo max|max)", re.IGNORECASE)

# 35 Cancelar suscripción
q35_RE = re.compile(r"(cancel|dar de baja|baja).*(suscrip|super|duolingo max|plan)", re.IGNORECASE)

# 36 Reembolso
q36_RE = re.compile(r"(reembols|devoluci[oó]n).*(suscrip|pago|plan)", re.IGNORECASE)

# 37 Código promocional
q37_RE = re.compile(r"(c[oó]dig|cup[oó]n|coupon).*(promo|promocional|canje|redeem)", re.IGNORECASE)

# 38 Lengua de señas
q38_RE = re.compile(r"(lengua|idioma) de se(n|ñ)as|se(n|ñ)as", re.IGNORECASE)

# 39 Añadirán más idiomas
q39_RE = re.compile(r"(nuev[oa]s? idiomas|a(n|ñ)adir[aán]? idiomas|m[aá]s idiomas)", re.IGNORECASE)

# 40 ¿Se puede aprender completamente solo con Duolingo?
q40_RE = re.compile(r"(se puede|puedo).*(aprender|dominar|completamente).*(solo|solamente).*(duolingo)", re.IGNORECASE)

# 41 Fluidez solo con Duolingo
q41_RE = re.compile(r"(fluidez|b2).*(solo|unicamente).*(duolingo)", re.IGNORECASE)

# 42 Planes que ofrece
q42_RE = re.compile(r"(planes?|suscrip).*(ofrece|hay|disponibles?)", re.IGNORECASE)

# 43 Qué incluye Gratis
q43_RE = re.compile(r"(que incluye|incluye).*(plan|modo).*gratis", re.IGNORECASE)

# 44 Qué incluye Súper
q44_RE = re.compile(r"(que incluye|incluye).*(super duolingo|super\\b)", re.IGNORECASE)

# 45 Qué incluye Súper Familia
q45_RE = re.compile(r"(que incluye|incluye).*(super familia|plan familiar)", re.IGNORECASE)

# 46 Prueba gratis
q46_RE = re.compile(r"(prueba|trial).*(gratis).*(super|s[uú]per)", re.IGNORECASE)

# 47 Cómo funciona la prueba
q47_RE = re.compile(r"(como funciona|funciona).*(prueba|trial).*(super|s[uú]per)", re.IGNORECASE)

# 48 Cuándo cobran después de la prueba
q48_RE = re.compile(r"(cuando|en que dia|cu[aá]ndo).*(cobran|me cobran).*(prueba|trial)", re.IGNORECASE)

# 49 Compromiso de permanencia
q49_RE = re.compile(r"(hay|existe).*(compromiso|permanencia)", re.IGNORECASE)

# 50 Cancelar app ≠ cancelar suscripción
q50_RE = re.compile(r"(elimin|desinstal).*(app|aplicaci[oó]n).*(cancel(a|aci[oó]n)?.*suscrip)", re.IGNORECASE)

# 51 Plan Familiar afecta progreso/racha
q51_RE = re.compile(r"(plan familiar).*(afect|pierdo).*(progreso|racha)", re.IGNORECASE)

# 52 Cuántas personas en Súper Familia
q52_RE = re.compile(r"(cuant[oa]s?).*(personas|miembros).*(super familia|plan familiar)", re.IGNORECASE)

# 53 Súper con anuncios
q53_RE = re.compile(r"(super|s[uú]per).*(anuncios?)", re.IGNORECASE)

# 54 Mi suscripción ayuda a mantener gratuito
q54_RE = re.compile(r"(mi suscripci[oó]n|pago).*(mantener|ayuda).*(gratuit|gratis)", re.IGNORECASE)

# 55 Plataformas / gestionar suscripción
q55_RE = re.compile(r"(plataformas?|dispositivos?|donde usar|gestionar suscrip|ios|android)", re.IGNORECASE)

# 56 Cuántos cursos hay
q56_RE = re.compile(r"(cuant[oa]s?).*(cursos).*(disponibles?|hay)", re.IGNORECASE)

# 57 Beneficios de Súper para progresar
q57_RE = re.compile(r"(beneficios?).*(super|s[uú]per).*(progres(ar|o)|avanzar|m[aá]s r[aá]pido)", re.IGNORECASE)

# --- NUEVOS atajos: precio/idiomas sueltos ---
qPRECIO_RE = re.compile(r"(precio|costo|vale|valor|cu[aá]nto cuesta|cu[aá]nto sale|tarifa).*(duolingo|super|max|suscrip|plan)?", re.IGNORECASE)
qIDIOMAS_SUELTO_RE = re.compile(r"^(idiomas?|lenguajes?)$", re.IGNORECASE)
qQUE_IDIOMAS_PUEDO_RE = re.compile(r"(que|cuales).*(idiomas?|lenguajes?).*(puedo|se puede|hay|ofrecen|aprender)", re.IGNORECASE)

# ---- fallback por palabras clave (si ningún regex matchea) ----
FALLBACK_KEYWORDS = [
    (re.compile(r"precio|costo|valor|cu[aá]nto (cuesta|sale)|tarifa"), 61),
    (re.compile(r"\bidiomas?\b|\blenguajes?\b"), 62),
    (re.compile(r"\bplanes?\b|\bsuscrip|\bgratis\b|\bfamiliar\b"), 42),
    (re.compile(r"cancel(ar|aci[oó]n)|dar de baja"), 35),
    (re.compile(r"reembols|devoluci[oó]n"), 36),
    (re.compile(r"privad"), 27),
    (re.compile(r"\bsegu(i|ir)|bloque|report"), 23),
    (re.compile(r"\belimin|borr|quitar.*cuenta"), 30),
    (re.compile(r"\breinici|reset.*curso"), 17),
    (re.compile(r"storie|historia(s)?\b"), 21),
    (re.compile(r"podcast"), 22),
    (re.compile(r"racha|streak"), 19),
    (re.compile(r"\bligas?\b|\bdivisiones?\b"), 20),
    (re.compile(r"\bmax\b|\bduolingo max\b"), 34),
]

def route_by_keywords(op: str):
    for rx, st in FALLBACK_KEYWORDS:
        if rx.search(op):
            dbg(f"Fallback -> state {st}")
            return st
    return None

def run_chatbot_duolingo():
    state = 0
    Salida = 1

    print("¡Hola! Soy el Chatbot no oficial sobre Duolingo. ¿En qué puedo ayudarte hoy?")

    while Salida:
        if state == 0:
            opcion_raw = input("Cuéntame tu duda (stories, racha, planes, precio, idiomas, etc.): ")
            opcion = normaliza(opcion_raw)

            if hola_RE.search(opcion):
                dbg("saludo/menu")
                print("Puedo ayudarte con: racha, ligas, stories, podcasts, cursos/idiomas, cambios de curso, seguir/bloquear, privacidad, planes (Gratis/Súper/Max), prueba, cancelaciones, códigos promocionales, etc.")
                state = 58
                continue

            # Router principal por regex
            ruta = None
            for regex, destino in [
                (q1_RE,1),(q2_RE,2),(q3_RE,3),(q4_RE,4),(q5_RE,5),(q6_RE,6),(q7_RE,7),(q8_RE,8),
                (q9_RE,9),(q10_RE,10),(q11_RE,11),(q12_RE,12),(q13_RE,13),(q14_RE,14),(q15_RE,15),(q16_RE,16),
                (q17_RE,17),(q18_RE,18),(q19_RE,19),(q20_RE,20),(q21_RE,21),(q22_RE,22),(q23_RE,23),(q24_RE,24),
                (q25_RE,25),(q26_RE,26),(q27_RE,27),(q28_RE,28),(q29_RE,29),(q30_RE,30),(q31_RE,31),(q32_RE,32),
                (q33_RE,33),(q34_RE,34),(q35_RE,35),(q36_RE,36),(q37_RE,37),(q38_RE,38),(q39_RE,39),(q40_RE,40),
                (q41_RE,41),(q42_RE,42),(q43_RE,43),(q44_RE,44),(q45_RE,45),(q46_RE,46),(q47_RE,47),(q48_RE,48),
                (q49_RE,49),(q50_RE,50),(q51_RE,51),(q52_RE,52),(q53_RE,53),(q54_RE,54),(q55_RE,55),(q56_RE,56),
                (q57_RE,57),
                (qPRECIO_RE,61),(qIDIOMAS_SUELTO_RE,62),(qQUE_IDIOMAS_PUEDO_RE,62),
            ]:
                if regex.search(opcion):
                    ruta = destino
                    break

            # Fallback si no hay match
            if ruta is None:
                ruta = route_by_keywords(opcion)

            if ruta is not None:
                dbg(f"Matched state {ruta}")
                state = ruta
            elif salir_RE.search(opcion):
                state = 59
            else:
                state = 60
            continue

        # ---- respuestas ----
        if state == 1:
            print("Duolingo fue creado por Luis von Ahn, Severin Hacker y el equipo de Duolingo."); state = 58; continue
        if state == 2:
            print("Ayuda oficial: Centro de Ayuda de Duolingo, Duolingo Wiki y discusiones de la comunidad."); state = 58; continue
        if state == 3:
            print("Duolingo gana dinero con el Duolingo English Test, suscripciones de Súper/Max y compras dentro de la app."); state = 58; continue
        if state == 4:
            print("Suelen salir actualizaciones cada pocas semanas; algunas funciones se prueban y pueden cambiar o desaparecer."); state = 58; continue
        if state == 5:
            print("Añadir demasiadas funciones vuelve la app confusa; por eso priorizan la simplicidad."); state = 58; continue
        if state == 6:
            print("Duolingo hace pruebas A/B: algunas funciones llegan solo a un grupo y luego deciden si las mantienen."); state = 58; continue
        if state == 7:
            print("Si una función no da buenos resultados, puede retirarse o pausarse para mejorarla."); state = 58; continue
        if state == 8:
            print("Actualizan cursos constantemente para hacerlos más efectivos y alinearte con nuevo contenido."); state = 58; continue
        if state == 9:
            print("Alrededor de 39 idiomas desde inglés (p. ej., español, francés, navajo, klingon). También catalán desde español e inglés desde >25 idiomas base."); state = 58; continue
        if state == 10:
            print("No hay límite: puedes estudiar varios idiomas en paralelo."); state = 58; continue
        if state == 11:
            print("Idiomas inventados: Klingon, Esperanto y Alto Valyrio."); state = 58; continue
        if state == 12:
            print("Lenguas en peligro: gaélico escocés, navajo y hawaiano."); state = 58; continue
        if state == 13:
            print("Sí: suajili y zulú. El curso de xhosa se retiró en 2023."); state = 58; continue
        if state == 14:
            print("Depende de tu objetivo: español o mandarín para el CV; francés para viajes; klingon/alto valyrio por diversión."); state = 58; continue
        if state == 15:
            print("Haz clic en la bandera, selecciona “+” y elige el idioma."); state = 58; continue
        if state == 16:
            print("Haz clic en la bandera y selecciona el curso que quieras practicar."); state = 58; continue
        if state == 17:
            print("Para reiniciar, elimina el curso en tu perfil y vuelve a agregarlo."); state = 58; continue
        if state == 18:
            print("Perfil → Configuración → Cursos → selecciona el idioma → Quitar."); state = 58; continue
        if state == 19:
            print("La racha es el número de días seguidos con lecciones completas; motiva a practicar a diario."); state = 58; continue
        if state == 20:
            print("Ligas y divisiones: competencias semanales donde compites con otros al ganar EXP."); state = 58; continue
        if state == 21:
            print("Stories: Desde inglés → fr, es, pt, de, it, ja. Para aprender inglés → de, es, fr, it, pt, tr, ru, uk, hi, ko, zh, ja. Además, proyecto Duostories con miles extra."); state = 58; continue
        if state == 22:
            print("Podcasts: español (para angloparlantes), francés (para angloparlantes), inglés para hispanohablantes e inglés para lusohablantes."); state = 58; continue
        if state == 23:
            print("Seguir: entra al perfil y pulsa “Seguir”. Dejar de seguir: “Siguiendo”. Bloquear: Perfil → Lista de amigos → Usuario → Bloquear. Reportar: Perfil → “Reportar usuario”."); state = 58; continue
        if state == 24:
            print("Ve a tu Perfil (app o web) para ver tu lista de amigos y sus estadísticas."); state = 58; continue
        if state == 25:
            print("Verifica tu correo, completa una lección si tu cuenta está inactiva o revisa si eres menor de 13 años o tienes el perfil privado."); state = 58; continue
        if state == 26:
            print("Cuando un amigo alcanza un objetivo, la app te permite enviar un mensaje de apoyo."); state = 58; continue
        if state == 27:
            print("Para hacerlo privado: Configuración de privacidad → desmarca “Volver público mi perfil”."); state = 58; continue
        if state == 28:
            print("En Configuración puedes editar usuario/correo y guardar; si ya están en uso, tendrás que cambiar a otro."); state = 58; continue
        if state == 29:
            print("Restablece tu contraseña en duolingo.com/forgot_password. Si usaste Google/Facebook, entra con ese correo."); state = 58; continue
        if state == 30:
            print("Solicita la eliminación en la Bóveda de datos de Duolingo; puede tardar hasta 30 días."); state = 58; continue
        if state == 31:
            print("Si recibiste un aviso oficial, cambia tus contraseñas y protege tus cuentas."); state = 58; continue
        if state == 32:
            print("Súper Duolingo: sin anuncios, vidas ilimitadas, práctica personalizada, repaso de errores, desafíos sin límites e intentos ilimitados en niveles legendarios."); state = 58; continue
        if state == 33:
            print("Plan Familiar de Súper: comparte con hasta 6 miembros."); state = 58; continue
        if state == 34:
            print("Duolingo Max: todo de Súper + funciones con IA: Explica mi respuesta, Juego de roles y Videollamadas con Lily."); state = 58; continue
        if state == 35:
            print("Cancela desde la plataforma de compra (Google Play o Apple). Eliminar la app o la cuenta NO cancela la suscripción."); state = 58; continue
        if state == 36:
            print("Reembolsos: en general no; depende de Apple o Google Play."); state = 58; continue
        if state == 37:
            print("Canjea en duolingo.com/redeem: introduce el código y sigue los pasos."); state = 58; continue
        if state == 38:
            print("Duolingo no ofrece lengua de señas. Considera clases locales o recursos en línea especializados."); state = 58; continue
        if state == 39:
            print("En 2022 añadieron criollo haitiano y zulú. Actualmente se enfocan en mejorar cursos y alinearlos a CEFR/ACTFL."); state = 58; continue
        if state == 40:
            print("No completamente: es un gran inicio, pero no sustituye la práctica real y estudio adicional."); state = 58; continue
        if state == 41:
            print("Algunos usuarios reportan niveles B2 (p. ej., español o francés), pero la mayoría necesita apoyo adicional."); state = 58; continue
        if state == 42:
            print("Planes disponibles: Gratis, Súper y Súper Familia."); state = 58; continue
        if state == 43:
            print("Plan Gratis: acceso al contenido básico de los cursos (con anuncios y sin ventajas de Súper)."); state = 58; continue
        if state == 44:
            print("Súper: sin anuncios, vidas ilimitadas, práctica personalizada, repaso de errores, desafíos sin límites y nivel legendario sin límites."); state = 58; continue
        if state == 45:
            print("Súper Familia: todos los beneficios de Súper para hasta 6 usuarios."); state = 58; continue
        if state == 46:
            print("Sí: prueba gratis de 1 semana para Súper."); state = 58; continue
        if state == 47:
            print("Prueba de Súper: Día 0 acceso completo · Día 5 recordatorio · Día 7 se cobra si no cancelas."); state = 58; continue
        if state == 48:
            print("Cobro tras la prueba: día 7. Cancela al menos 24 horas antes para evitar el cargo."); state = 58; continue
        if state == 49:
            print("No hay compromiso de permanencia: puedes cancelar cuando quieras."); state = 58; continue
        if state == 50:
            print("No: eliminar/desinstalar la app o tu cuenta NO cancela la suscripción; cancélala en la tienda correspondiente."); state = 58; continue
        if state == 51:
            print("Entrar o salir del Plan Familiar no afecta tu progreso ni tu racha."); state = 58; continue
        if state == 52:
            print("Súper Familia puede usarse hasta por 6 usuarios."); state = 58; continue
        if state == 53:
            print("Súper Duolingo no tiene anuncios; el plan Gratis sí incluye anuncios."); state = 58; continue
        if state == 54:
            print("Sí: tu suscripción ayuda a mantener la educación gratuita para millones de usuarios."); state = 58; continue
        if state == 55:
            print("Usa y gestiona tu suscripción en iOS (App Store) y Android (Google Play)."); state = 58; continue
        if state == 56:
            print("Hay más de 100 cursos de idiomas disponibles en Duolingo."); state = 58; continue
        if state == 57:
            print("Para progresar más rápido: vidas ilimitadas, práctica personalizada, repaso de errores, nivel legendario sin límites y sin anuncios."); state = 58; continue

        # ---- respuestas nuevas ----
        if state == 61:
            print("Precios: varían según país/tienda (App Store o Google Play) y plan (Súper o Súper Familia). "
                  "Consulta el precio exacto en la tienda de tu dispositivo. Recuerda: existe el plan Gratis con $0, "
                  "y hay prueba gratis de 7 días para Súper.")
            state = 58; continue

        if state == 62:
            print("Duolingo ofrece más de 100 cursos. Desde inglés, hay ~39 idiomas (p. ej., español, francés, navajo, klingon). "
                  "También puedes aprender catalán desde español y hay inglés desde más de 25 idiomas base.")
            state = 58; continue

        # ---- menú “¿algo más?” ----
        if state == 58:
            opcion_raw = input("¿Necesitas ayuda con algo más? (escribe 'salir' para terminar): ")
            opcion = normaliza(opcion_raw)

            if salir_RE.search(opcion):
                state = 59
                continue

            if hola_RE.search(opcion):
                dbg("saludo/menu loop")
                print("Temas: racha, ligas, stories, podcasts, idiomas, privacidad, seguir/bloquear, planes, prueba, cancelar, reembolso, códigos, etc.")
                state = 58
                continue

            ruta = None
            for regex, destino in [
                (q1_RE,1),(q2_RE,2),(q3_RE,3),(q4_RE,4),(q5_RE,5),(q6_RE,6),(q7_RE,7),(q8_RE,8),
                (q9_RE,9),(q10_RE,10),(q11_RE,11),(q12_RE,12),(q13_RE,13),(q14_RE,14),(q15_RE,15),(q16_RE,16),
                (q17_RE,17),(q18_RE,18),(q19_RE,19),(q20_RE,20),(q21_RE,21),(q22_RE,22),(q23_RE,23),(q24_RE,24),
                (q25_RE,25),(q26_RE,26),(q27_RE,27),(q28_RE,28),(q29_RE,29),(q30_RE,30),(q31_RE,31),(q32_RE,32),
                (q33_RE,33),(q34_RE,34),(q35_RE,35),(q36_RE,36),(q37_RE,37),(q38_RE,38),(q39_RE,39),(q40_RE,40),
                (q41_RE,41),(q42_RE,42),(q43_RE,43),(q44_RE,44),(q45_RE,45),(q46_RE,46),(q47_RE,47),(q48_RE,48),
                (q49_RE,49),(q50_RE,50),(q51_RE,51),(q52_RE,52),(q53_RE,53),(q54_RE,54),(q55_RE,55),(q56_RE,56),
                (q57_RE,57),
                (qPRECIO_RE,61),(qIDIOMAS_SUELTO_RE,62),(qQUE_IDIOMAS_PUEDO_RE,62),
            ]:
                if regex.search(opcion):
                    ruta = destino
                    break

            if ruta is None:
                ruta = route_by_keywords(opcion)

            if ruta is not None:
                dbg(f"Matched state {ruta} (menu loop)")
                state = ruta
            else:
                state = 60
            continue

        # ---- salir ----
        if state == 59:
            print("¡Gracias por contactarme! Fue un placer ayudarte. ")
            Salida = 0
            continue

        # ---- no entendido ----
        if state == 60:
            print("No logré entender tu consulta. ¿Podrías intentarlo de otra forma? (prueba: 'precio', 'idiomas', 'planes', 'racha')")
            state = 0
            continue

if __name__ == "__main__":
    run_chatbot_duolingo()
