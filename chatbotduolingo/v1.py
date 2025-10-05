# ChatbotDuolingo_FSM.py
# -*- coding: utf-8 -*-
import re
import unicodedata

def normaliza(txt: str) -> str:
    txt = (txt or "").strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    return txt.lower()

# ---- patrones ----
salir_RE = re.compile(r"^(no|salir|me equivoque|perdon|adios|deseo (salir|interrumpir))$", re.IGNORECASE)

# 1 ¿Quién creó Duolingo?
q1_RE  = re.compile(r"(quien|quienes|creador(es)?|fundo|fundador(es)?)\s.*duolingo|creo.*duolingo", re.IGNORECASE)

# 2 ¿Dónde puedo obtener ayuda oficial?
q2_RE  = re.compile(r"(donde|donde puedo|ayuda|soporte|asistencia).*(duolingo|oficial|centro|wiki|comunidad)", re.IGNORECASE)

# 3 ¿Cuál es el modelo de negocio de Duolingo?
q3_RE  = re.compile(r"(modelo|como gana|ingresos|negocio).*(duolingo)", re.IGNORECASE)

# 4 ¿Cada cuánto salen nuevas actualizaciones?
q4_RE  = re.compile(r"(cada cuanto|frecuencia|cuando).*(actualiz|updates?)", re.IGNORECASE)

# 5 ¿Por qué Duolingo no tiene X función opcional?
q5_RE  = re.compile(r"(por que|porque).*(no (tiene|hay)).*(funcion|feature|opcional)", re.IGNORECASE)

# 6 ¿Por qué yo tengo una función que mis amigos no tienen?
q6_RE  = re.compile(r"(tengo.*funcion.*(amigos?|otros)|mis amigos.*no (tienen|ven)|prueba(s)? a/b|experimentos?)", re.IGNORECASE)

# 7 Tenía una función y ya no la tengo, ¿por qué?
q7_RE  = re.compile(r"(tenia|tenia).*funcion.*ya no|desaparecio.*funcion", re.IGNORECASE)

# 8 ¿Por qué cambió mi curso?
q8_RE  = re.compile(r"(por que|porque).*(cambio).*curso|mi curso cambio", re.IGNORECASE)

# 9 ¿Cuántos idiomas ofrece Duolingo?
q9_RE  = re.compile(r"(cuantos?|cuantas?).*idiomas?.*(ofrece|hay)", re.IGNORECASE)

# 10 ¿Cuántos idiomas puedo aprender a la vez?
q10_RE = re.compile(r"(cuantos?|cuantas?).*idiomas?.*(a la vez|simultan|paralelo)|estudiar.*varios", re.IGNORECASE)

# 11 ¿Qué idiomas inventados enseña Duolingo?
q11_RE = re.compile(r"(idiomas?|lenguas?).*(inventad|construid|fictici|cread).*", re.IGNORECASE)

# 12 ¿Qué lenguas en peligro puedo aprender?
q12_RE = re.compile(r"(lenguas?|idiomas?).*(en peligro|amenazad|revitaliz)", re.IGNORECASE)

# 13 ¿Duolingo tiene idiomas africanos?
q13_RE = re.compile(r"(idiomas?).*(african|africa)|suajili|zulu|zul(u|u)|xhosa", re.IGNORECASE)

# 14 ¿Qué idioma debería aprender?
q14_RE = re.compile(r"(que|cual).*(idioma).*(deberia|me conviene|recomiendas?)", re.IGNORECASE)

# 15 ¿Cómo empiezo otro curso?
q15_RE = re.compile(r"(como|c(o|o)mo).*(empezar|agregar|iniciar).*(otro|nuevo).*curso", re.IGNORECASE)

# 16 ¿Cómo cambio de idioma?
q16_RE = re.compile(r"(cambiar|switch|alternar).*(idioma|curso)", re.IGNORECASE)

# 17 ¿Cómo reinicio un curso?
q17_RE = re.compile(r"(reiniciar|empezar de cero|reset).*curso", re.IGNORECASE)

# 18 ¿Cómo elimino un idioma?
q18_RE = re.compile(r"(eliminar|quitar|borrar).*(idioma|curso)", re.IGNORECASE)

# 19 ¿Qué es la racha?
q19_RE = re.compile(r"(que|que es).*(racha|streak)", re.IGNORECASE)

# 20 ¿Qué son las Ligas y divisiones?
q20_RE = re.compile(r"(ligas?|divisiones?|clasificac)", re.IGNORECASE)

# 21 ¿Qué cursos tienen Stories?
q21_RE = re.compile(r"(stories|historias).*(que cursos|cuales idiomas|disponibles)", re.IGNORECASE)

# 22 ¿Qué idiomas tienen podcasts?
q22_RE = re.compile(r"(podcasts?).*(idiomas?|cuales)", re.IGNORECASE)

# 23 ¿Cómo busco, sigo o bloqueo usuarios?
q23_RE = re.compile(r"(buscar|seguir|dejar de seguir|bloquear|reportar).*(usuarios?|amigos?)", re.IGNORECASE)

# 24 ¿Dónde veo a mis amigos?
q24_RE = re.compile(r"(donde|donde veo).*(amigos|lista de amigos)", re.IGNORECASE)

# 25 ¿Qué pasa si no puedo seguir a alguien?
q25_RE = re.compile(r"(no puedo|no me deja|problema).*(seguir).*alguien", re.IGNORECASE)

# 26 ¿Cómo envío felicitaciones?
q26_RE = re.compile(r"(enviar|mandar).*(felicit|congrats|mensaje de apoyo)", re.IGNORECASE)

# 27 ¿Cómo hago privado mi perfil?
q27_RE = re.compile(r"(hacer|poner|volver).*(privad).*(perfil)", re.IGNORECASE)

# 28 ¿Cómo cambio mi nombre de usuario o correo?
q28_RE = re.compile(r"(cambiar|editar|actualizar).*(nombre de usuario|usuario|correo|email)", re.IGNORECASE)

# 29 Problemas para acceder a mi cuenta
q29_RE = re.compile(r"(no puedo|problemas?).*(acceder|iniciar sesion|entrar|login|cuenta)", re.IGNORECASE)

# 30 ¿Cómo elimino mi cuenta y mis datos?
q30_RE = re.compile(r"(eliminar|borrar).*(cuenta|datos|informacion)", re.IGNORECASE)

# 31 ¿Qué hago si mis datos se vieron comprometidos?
q31_RE = re.compile(r"(datos|seguridad|comprometidos?|filtracion|brecha)", re.IGNORECASE)

# 32 ¿Qué es Súper Duolingo?
q32_RE = re.compile(r"(que es|beneficios?).*(super duolingo|super)", re.IGNORECASE)

# 33 ¿Qué es el Plan Familiar de Súper?
q33_RE = re.compile(r"(plan|familiar).*(super)", re.IGNORECASE)

# 34 ¿Qué es Duolingo Max?
q34_RE = re.compile(r"(que es).*(duolingo max|max)", re.IGNORECASE)

# 35 ¿Cómo cancelo mi suscripción?
q35_RE = re.compile(r"(cancelar|dar de baja).*(suscrip|super|duolingo max)", re.IGNORECASE)

# 36 ¿Puedo pedir reembolso?
q36_RE = re.compile(r"(reembolso|devolucion).*(suscrip|pago)", re.IGNORECASE)

# 37 ¿Cómo uso un código promocional?
q37_RE = re.compile(r"(codigo|cupon|coupon).*(promo|promocional|canjear|redeem)", re.IGNORECASE)

# 38 ¿Se puede aprender lengua de señas?
q38_RE = re.compile(r"(lengua|idioma) de sen(as|as)|se(na|na)s", re.IGNORECASE)

# 39 ¿Añadirán más idiomas?
q39_RE = re.compile(r"(nuevos? idiomas|anadiran? idiomas|mas idiomas)", re.IGNORECASE)

# 40 ¿Se puede aprender completamente solo con Duolingo?
q40_RE = re.compile(r"(se puede|puedo).*(aprender|dominar|completamente|solo con duolingo)", re.IGNORECASE)

# 41 ¿Alguien logró fluidez solo con Duolingo?
q41_RE = re.compile(r"(fluidez|b2).*(solo|unicamente).*(duolingo)", re.IGNORECASE)

# 42 ¿Qué planes ofrece Duolingo?
q42_RE = re.compile(r"(planes?|suscrip).*(ofrece|hay)", re.IGNORECASE)

# 43 ¿Qué incluye el plan Gratis?
q43_RE = re.compile(r"(que incluye|incluye).*(plan|modo).*gratis", re.IGNORECASE)

# 44 ¿Qué incluye Súper?
q44_RE = re.compile(r"(que incluye|incluye).*(super duolingo|super)", re.IGNORECASE)

# 45 ¿Qué incluye Súper Familia?
q45_RE = re.compile(r"(que incluye|incluye).*(super familia|plan familiar)", re.IGNORECASE)

# 46 ¿Puedo probar Súper gratis?
q46_RE = re.compile(r"(prueba|trial).*(gratis).*(super)", re.IGNORECASE)

# 47 ¿Cómo funciona la prueba gratis?
q47_RE = re.compile(r"(como funciona|funciona).*(prueba|trial).*(super)", re.IGNORECASE)

# 48 ¿Cuándo me cobran después de la prueba?
q48_RE = re.compile(r"(cuando|en que dia).*(cobran|me cobran).*(prueba|trial)", re.IGNORECASE)

# 49 ¿Hay compromiso de permanencia?
q49_RE = re.compile(r"(hay|existe).*(compromiso|permanencia)", re.IGNORECASE)

# 50 ¿Cancelar la app cancela mi suscripción?
q50_RE = re.compile(r"(eliminar|desinstalar).*(app|aplicacion).*(cancela.*suscrip)", re.IGNORECASE)

# 51 ¿El Plan Familiar afecta mi progreso o racha?
q51_RE = re.compile(r"(plan familiar).*(afecta|pierdo).*(progreso|racha)", re.IGNORECASE)

# 52 ¿Cuántas personas pueden usar Súper Familia?
q52_RE = re.compile(r"(cuantos?|cuantas?).*(personas|miembros).*(super familia|plan familiar)", re.IGNORECASE)

# 53 ¿Súper Duolingo tiene anuncios?
q53_RE = re.compile(r"(super).*(anuncios?)", re.IGNORECASE)

# 54 ¿Mi suscripción ayuda a mantener Duolingo gratuito?
q54_RE = re.compile(r"(mi suscripcion|pago).*(mantener|ayuda).*(gratuito|gratis)", re.IGNORECASE)

# 55 ¿En qué plataformas puedo usar / gestionar?
q55_RE = re.compile(r"(plataformas?|dispositivos?|donde usar|gestionar suscrip)", re.IGNORECASE)

# 56 ¿Cuántos cursos hay disponibles en Duolingo?
q56_RE = re.compile(r"(cuantos?|cuantas?).*(cursos).*(disponibles|hay)", re.IGNORECASE)

# 57 Beneficios de Súper para progresar más rápido
q57_RE = re.compile(r"(beneficios?).*(super).*(progres(ar|o)|avanzar|mas rapido)", re.IGNORECASE)

def run_chatbot_duolingo():
    # ---- máquina de estados ----
    state = 0
    Salida = 1

    print("¡Hola! Soy el Chatbot no oficial sobre Duolingo. ¿En qué puedo ayudarte hoy?")

    while Salida:
        if state == 0:
            opcion = normaliza(input("Cuéntame tu duda (stories, racha, planes, cancelar suscripción, etc.): "))

            if q1_RE.search(opcion):    state = 1
            elif q2_RE.search(opcion):  state = 2
            elif q3_RE.search(opcion):  state = 3
            elif q4_RE.search(opcion):  state = 4
            elif q5_RE.search(opcion):  state = 5
            elif q6_RE.search(opcion):  state = 6
            elif q7_RE.search(opcion):  state = 7
            elif q8_RE.search(opcion):  state = 8
            elif q9_RE.search(opcion):  state = 9
            elif q10_RE.search(opcion): state = 10
            elif q11_RE.search(opcion): state = 11
            elif q12_RE.search(opcion): state = 12
            elif q13_RE.search(opcion): state = 13
            elif q14_RE.search(opcion): state = 14
            elif q15_RE.search(opcion): state = 15
            elif q16_RE.search(opcion): state = 16
            elif q17_RE.search(opcion): state = 17
            elif q18_RE.search(opcion): state = 18
            elif q19_RE.search(opcion): state = 19
            elif q20_RE.search(opcion): state = 20
            elif q21_RE.search(opcion): state = 21
            elif q22_RE.search(opcion): state = 22
            elif q23_RE.search(opcion): state = 23
            elif q24_RE.search(opcion): state = 24
            elif q25_RE.search(opcion): state = 25
            elif q26_RE.search(opcion): state = 26
            elif q27_RE.search(opcion): state = 27
            elif q28_RE.search(opcion): state = 28
            elif q29_RE.search(opcion): state = 29
            elif q30_RE.search(opcion): state = 30
            elif q31_RE.search(opcion): state = 31
            elif q32_RE.search(opcion): state = 32
            elif q33_RE.search(opcion): state = 33
            elif q34_RE.search(opcion): state = 34
            elif q35_RE.search(opcion): state = 35
            elif q36_RE.search(opcion): state = 36
            elif q37_RE.search(opcion): state = 37
            elif q38_RE.search(opcion): state = 38
            elif q39_RE.search(opcion): state = 39
            elif q40_RE.search(opcion): state = 40
            elif q41_RE.search(opcion): state = 41
            elif q42_RE.search(opcion): state = 42
            elif q43_RE.search(opcion): state = 43
            elif q44_RE.search(opcion): state = 44
            elif q45_RE.search(opcion): state = 45
            elif q46_RE.search(opcion): state = 46
            elif q47_RE.search(opcion): state = 47
            elif q48_RE.search(opcion): state = 48
            elif q49_RE.search(opcion): state = 49
            elif q50_RE.search(opcion): state = 50
            elif q51_RE.search(opcion): state = 51
            elif q52_RE.search(opcion): state = 52
            elif q53_RE.search(opcion): state = 53
            elif q54_RE.search(opcion): state = 54
            elif q55_RE.search(opcion): state = 55
            elif q56_RE.search(opcion): state = 56
            elif q57_RE.search(opcion): state = 57
            elif salir_RE.search(opcion): state = 59
            else: state = 60
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
            print("Configura privacidad: desmarca “Volver público mi perfil”."); state = 58; continue
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

        # ---- menú “¿algo más?” ----
        if state == 58:
            opcion = normaliza(input("¿Necesitas ayuda con algo más? (escribe 'salir' para terminar): "))
            if salir_RE.search(opcion): state = 59
            elif q1_RE.search(opcion):  state = 1
            elif q2_RE.search(opcion):  state = 2
            elif q3_RE.search(opcion):  state = 3
            elif q4_RE.search(opcion):  state = 4
            elif q5_RE.search(opcion):  state = 5
            elif q6_RE.search(opcion):  state = 6
            elif q7_RE.search(opcion):  state = 7
            elif q8_RE.search(opcion):  state = 8
            elif q9_RE.search(opcion):  state = 9
            elif q10_RE.search(opcion): state = 10
            elif q11_RE.search(opcion): state = 11
            elif q12_RE.search(opcion): state = 12
            elif q13_RE.search(opcion): state = 13
            elif q14_RE.search(opcion): state = 14
            elif q15_RE.search(opcion): state = 15
            elif q16_RE.search(opcion): state = 16
            elif q17_RE.search(opcion): state = 17
            elif q18_RE.search(opcion): state = 18
            elif q19_RE.search(opcion): state = 19
            elif q20_RE.search(opcion): state = 20
            elif q21_RE.search(opcion): state = 21
            elif q22_RE.search(opcion): state = 22
            elif q23_RE.search(opcion): state = 23
            elif q24_RE.search(opcion): state = 24
            elif q25_RE.search(opcion): state = 25
            elif q26_RE.search(opcion): state = 26
            elif q27_RE.search(opcion): state = 27
            elif q28_RE.search(opcion): state = 28
            elif q29_RE.search(opcion): state = 29
            elif q30_RE.search(opcion): state = 30
            elif q31_RE.search(opcion): state = 31
            elif q32_RE.search(opcion): state = 32
            elif q33_RE.search(opcion): state = 33
            elif q34_RE.search(opcion): state = 34
            elif q35_RE.search(opcion): state = 35
            elif q36_RE.search(opcion): state = 36
            elif q37_RE.search(opcion): state = 37
            elif q38_RE.search(opcion): state = 38
            elif q39_RE.search(opcion): state = 39
            elif q40_RE.search(opcion): state = 40
            elif q41_RE.search(opcion): state = 41
            elif q42_RE.search(opcion): state = 42
            elif q43_RE.search(opcion): state = 43
            elif q44_RE.search(opcion): state = 44
            elif q45_RE.search(opcion): state = 45
            elif q46_RE.search(opcion): state = 46
            elif q47_RE.search(opcion): state = 47
            elif q48_RE.search(opcion): state = 48
            elif q49_RE.search(opcion): state = 49
            elif q50_RE.search(opcion): state = 50
            elif q51_RE.search(opcion): state = 51
            elif q52_RE.search(opcion): state = 52
            elif q53_RE.search(opcion): state = 53
            elif q54_RE.search(opcion): state = 54
            elif q55_RE.search(opcion): state = 55
            elif q56_RE.search(opcion): state = 56
            elif q57_RE.search(opcion): state = 57
            else: state = 60
            continue

        # ---- salir ----
        if state == 59:
            print("¡Gracias por contactarme! Fue un placer ayudarte. 🟢")
            Salida = 0
            continue

        # ---- no entendido ----
        if state == 60:
            print("No logré entender tu consulta. ¿Podrías intentarlo de nuevo?")
            state = 0
            continue

# permite ejecutar este módulo directo si quieres
if __name__ == "__main__":
    run_chatbot_duolingo()
