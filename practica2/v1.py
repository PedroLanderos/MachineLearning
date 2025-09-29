from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random
import math


GEN_MIN, GEN_MAX = 1, 9
NUM_GENES = 20
MUTACION_MIN, MUTACION_MAX = 0.10, 0.90



@dataclass
class Individuo:
    id: int
    genes: List[int]
    porcentaje_mutacion: float
    padres: Optional[Tuple[int, int]] = None

PoblacionTotal = Dict[int, Individuo]  
Generaciones = List[List[int]]         

def CrearPoblacionInicial(n = 100):
    poblacion = []

    for i in range (1, n + 1):
        genes = [random.randint(GEN_MIN, GEN_MAX) for _ in range(NUM_GENES)]
        porcentaje_mutacion = random.uniform(MUTACION_MIN, MUTACION_MAX)
        individuo = Individuo(
            id=i,
            genes=genes,
            porcentaje_mutacion=porcentaje_mutacion,
            padres=None
        )
        poblacion.append(individuo)
    return poblacion


def FormarParejas(poblacion: List[Individuo]) -> List[Tuple[Individuo, Individuo]]:
    if len(poblacion) % 2 != 0:
        raise ValueError("La poblacion inicial no es par")
    
    individuos = poblacion[:]
    random.shuffle(individuos)

    parejas = []
    for i in range(0, len(individuos), 2):
        pareja = (individuos[i], individuos[i+1])
        parejas.append(pareja)
    
    return parejas

def SonHermanos(a: Individuo, b: Individuo) -> bool:
    return (a.padres is not None) and (b.padres is not None) and (a.padres == b.padres)

def ElegirReemplazoNoHermano(fijo: Individuo, poblacion: List[Individuo]) -> Individuo:
    intentos = 0
    while intentos < 10_000:
        candidato = random.choice(poblacion)
        if candidato.id != fijo.id and not SonHermanos(fijo, candidato):
            return candidato
        intentos += 1
    raise RuntimeError("No se encontró reemplazo no-hermano tras muchos intentos.")

def CrearHijos(padre_a: Individuo, padre_b: Individuo, poblacion: List[Individuo], id_inicio: int) -> Tuple[List[Individuo], Tuple[Individuo, Individuo]]:
    # Asegurar que no sean la misma persona
    if padre_a.id == padre_b.id:
        # Fuerza reemplazo del segundo
        padre_b = ElegirReemplazoNoHermano(padre_a, poblacion)

    # Evitar cruces entre hermanos
    if SonHermanos(padre_a, padre_b):
        # Reemplazamos aleatoriamente a uno de los dos
        if random.random() < 0.5:
            padre_a = ElegirReemplazoNoHermano(padre_b, poblacion)
        else:
            padre_b = ElegirReemplazoNoHermano(padre_a, poblacion)

    # Promedios gen a gen
    promedios = [(g1 + g2) / 2 for g1, g2 in zip(padre_a.genes, padre_b.genes)]

    # Hijos: uno con floor y otro con ceil
    genes_abajo = [int(math.floor(x)) for x in promedios]
    genes_arriba = [int(math.ceil(x)) for x in promedios]

    # Padres normalizados como (id_padre_a, id_padre_b) en el orden dado
    tupla_padres = (padre_a.id, padre_b.id)

    hijo_abajo = Individuo(
        id=id_inicio,
        genes=genes_abajo,
        porcentaje_mutacion=random.uniform(MUTACION_MIN, MUTACION_MAX),
        padres=tupla_padres
    )
    hijo_arriba = Individuo(
        id=id_inicio + 1,
        genes=genes_arriba,
        porcentaje_mutacion=random.uniform(MUTACION_MIN, MUTACION_MAX),
        padres=tupla_padres
    )

    return [hijo_abajo, hijo_arriba], (padre_a, padre_b)

def EsHumanoPerfecto(individuo: Individuo) -> bool:
    return all(g == GEN_MAX for g in individuo.genes)

def HayHumanoPerfecto(poblacion: List[Individuo]) -> Tuple[bool, Optional[Individuo]]:
    for ind in poblacion:
        if EsHumanoPerfecto(ind):
            return True, ind
    return False, None

def AplicarMutacionUnaVez(individuo: Individuo, p_mejora: float = 0.80, p_empeora: float = 0.10) -> bool:
    p_aleatoria = 1.0 - (p_mejora + p_empeora)
    if p_aleatoria < 0:
        raise ValueError("Las probabilidades no son válidas")
    if random.random() <= individuo.porcentaje_mutacion:
        idx = random.randrange(NUM_GENES)
        v = individuo.genes[idx]
        r = random.random()
        if r < p_mejora and v < GEN_MAX:
            nuevo = random.randint(v + 1, GEN_MAX)
        elif r < p_mejora + p_empeora and v > GEN_MIN:
            nuevo = random.randint(GEN_MIN, v - 1)
        else:
            nuevo = v
            while nuevo == v:
                nuevo = random.randint(GEN_MIN, GEN_MAX)
        individuo.genes[idx] = nuevo
        return True
    return False



def CrearHijosParaParejas(
    parejas: List[Tuple[Individuo, Individuo]],
    poblacion: List[Individuo],
    siguiente_id: int,
    aplicar_mutacion: bool = True
) -> Tuple[List[Individuo], int]:
    
    nuevos_hijos: List[Individuo] = []

    for p_a, p_b in parejas:
        hijos, _ = CrearHijos(p_a, p_b, poblacion, siguiente_id)
        siguiente_id += 2

        if aplicar_mutacion:
            for h in hijos:
                AplicarMutacionUnaVez(h)

        nuevos_hijos.extend(hijos)

    return nuevos_hijos, siguiente_id


def InicializarEstructuras(poblacion_inicial: List[Individuo]) -> Tuple[PoblacionTotal, Generaciones, int]:
    poblacion_total: PoblacionTotal = {ind.id: ind for ind in poblacion_inicial}
    generaciones: Generaciones = [[ind.id for ind in poblacion_inicial]]
    siguiente_id = (max(poblacion_total.keys()) + 1) if poblacion_total else 1
    return poblacion_total, generaciones, siguiente_id


def ActualizarEstructurasTrasGeneracion(
    poblacion_total: PoblacionTotal,
    generaciones: Generaciones,
    nuevos_hijos: List[Individuo]
) -> Tuple[bool, Optional[Individuo]]:
    # Registrar en el índice global
    for h in nuevos_hijos:
        poblacion_total[h.id] = h

    # Registrar la nueva generación por ids
    generaciones.append([h.id for h in nuevos_hijos])

    # Verificar si apareció un humano perfecto en esta generación
    for h in nuevos_hijos:
        if EsHumanoPerfecto(h):
            return True, h
    return False, None

def EjecutarGeneracion(
    poblacion_actual: List[Individuo],
    poblacion_total: PoblacionTotal,
    generaciones: Generaciones,
    siguiente_id: int,
    aplicar_mutacion: bool = True
) -> Tuple[List[Individuo], int, bool, Optional[Individuo]]:
    
    parejas = FormarParejas(poblacion_actual)
    nuevos_hijos, siguiente_id = CrearHijosParaParejas(
        parejas, poblacion_actual, siguiente_id, aplicar_mutacion=aplicar_mutacion
    )
    hay_perfecto, perfecto = ActualizarEstructurasTrasGeneracion(
        poblacion_total, generaciones, nuevos_hijos
    )
    return nuevos_hijos, siguiente_id, hay_perfecto, perfecto



def SumaTotalGenes(individuo: Individuo) -> int:
    return sum(individuo.genes)

def MejorDePoblacion(poblacion: List[Individuo]) -> Tuple[Individuo, int]:
    mejor = max(poblacion, key=SumaTotalGenes)
    return mejor, SumaTotalGenes(mejor)

def SimularHastaPerfecto(
    poblacion_inicial: List[Individuo],
    max_generaciones: int = 1000,
    aplicar_mutacion: bool = True,
    semilla: Optional[int] = None,
    imprimir_progreso: bool = True
) -> Tuple[bool, Optional[Individuo], Generaciones, PoblacionTotal, int, int]:
    if semilla is not None:
        random.seed(semilla)

    poblacion_total, generaciones, siguiente_id = InicializarEstructuras(poblacion_inicial)

    if imprimir_progreso:
        mejor0, suma0 = MejorDePoblacion(poblacion_inicial)
        print(f"Generación 0 | Mejor suma de genes: {suma0}/180 | Mejor ID: {mejor0.id}")

    hay_ini, perfecto_ini = HayHumanoPerfecto(poblacion_inicial)
    if hay_ini:
        if imprimir_progreso:
            print(f"¡Humano perfecto encontrado en Generación 0!")
            print(f"ID: {perfecto_ini.id} | Padres: {perfecto_ini.padres}")
        return True, perfecto_ini, generaciones, poblacion_total, 0, siguiente_id

    poblacion_actual = poblacion_inicial
    generaciones_procesadas = 0

    for gen_idx in range(1, max_generaciones + 1):
        poblacion_actual, siguiente_id, hay_perf, perfecto = EjecutarGeneracion(
            poblacion_actual, poblacion_total, generaciones, siguiente_id, aplicar_mutacion=aplicar_mutacion
        )
        generaciones_procesadas += 1

        if imprimir_progreso:
            mejor, suma = MejorDePoblacion(poblacion_actual)
            print(f"Generación {gen_idx} | Mejor suma de genes: {suma}/180 | Mejor ID: {mejor.id}")

        if hay_perf:
            if imprimir_progreso:
                print(f"¡Humano perfecto encontrado en Generación {gen_idx}!")
                print(f"ID: {perfecto.id} | Padres: {perfecto.padres}")
            return True, perfecto, generaciones, poblacion_total, generaciones_procesadas, siguiente_id

    if imprimir_progreso:
        print(f"No se encontró un humano perfecto tras {max_generaciones} generaciones.")
    return False, None, generaciones, poblacion_total, generaciones_procesadas, siguiente_id

poblacion0 = CrearPoblacionInicial(100)
encontro, perfecto, generaciones, poblacion_total, gens_proc, siguiente_id = SimularHastaPerfecto(
    poblacion_inicial=poblacion0,
    max_generaciones=100000,
    aplicar_mutacion=True,
    semilla=42,
    imprimir_progreso=True
)