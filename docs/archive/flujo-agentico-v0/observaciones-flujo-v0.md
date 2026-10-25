# Observaciones de David al flujo agéntico v0 (OpenCode + DeepSeek), 9–23 oct 2026

> Digitalización de más de 30 hojas manuscritas. Es el insumo que llevó al ADR-0001 (simplificar el flujo:
> determinismo por herramientas). Se conserva como evidencia de revisión humana crítica del trabajo generado
> por IA (propuesta, sección 4). Al final aparece el "plan de ataque" que otra IA propuso y que fue descartado.

---

Modificaciones / ajustes confirmados y Observaciones, Flujo Agéntico

Convenciones:

> • Premisas: Afirmaciones validables que, de acuerdo con lo condensado
> en plan-redactor.md, se le instruye al agente que debe extraerlas del
> borrador “0” del plan. Se trata de oraciones que pueden ser
> “confirmadas” al consultar fuentes de autoridad que contengan
> información relacionada con el contenido de la premisa: p. ej. “1 + 1
> = 2” -\> Existe sólida evidencia en diversas fuentes que respalda esta
> afirmación, por tanto, se puede decir que es “confirmada”. P. ej. 2.
> “1+1=3” -\> Existe sólida evidencia en diversas fuentes que desmienten
> esta afirmación, por tanto, se puede decir que es “contradicha”. P.
> ej. 3. “Una muy buena forma de combatir deuda técnica asociada a
> scattered auth logic en un MVP es emplear una clase de políticas de
> acceso de los usuarios” Existe sólida evidencia en diversas fuentes
> que respalda esta afirmación, por tanto, se puede decir que es
> “confirmada”. P. ej. 4. “La mejor forma de solucionar deuda técnica
> asociada con lógica de autorización dispersa en un proyecto de
> Fast-API es crear un flujo agéntico desde 0 con ayuda de la API de
> deepseek + análisis propio de cerebro humano” -\> es una afimación
> demasiado específica y puede que no existan fuentes de autoridad con
> sólida evidencia que respalde esta afirmación. En caso de no existir
> dichas fuentes, la afirmación no puede ser contrastada con ninguna
> fuente, y por tanto se puede decir que es una afirmación “no
> confirmable ante fuentes externas”. Es extremadamente normal que
> afirmaciones como la del ejemplo 3 abunden, y dependerá del criterio
> del LLM en conjunto con la auditoría humana a dicho criterio que las
> cosas salgan bien o no tan bien.
>
> Las Premisas se utilizan en este fujo agéntico -plan-redactor.md, paso
> 6, sección c- para validar qué tan bien acotado quedó el plan y
> también para validar decisiones relacionadas con detalles técnicos de
> la implementación frente a fuentes confiables, lo que permite reducir
> la posibilidad de introducir código desactualizado, propenso a
> errores/bugs o deprecado.
>
> • Criterios: Afirmaciones validables que, de acuerdo con los
> contenidos de plan-redactor.md, en conjunto deben constituir “un todo”
> que representa correctamente el molde del que debe salir cada plan. Se
> emplean en el apéndice c del paso 6, para evaluar el borrador “1” del
> plan y verificar que resuelve el problema correcto, pero de la forma
> correcta.
>
> 1.) \[DOCUMENTACIÓN\] Dejar indicado explícitamente a dónde el agente
> debe ir a documentar cada una de las piezas de información asociada
> con la confirmación/contradicción de premisas y/o criterios (inserción
> en bitácora, sección residuales, en apéndices específicos de sección
> fuentes de autoridad, etc, (aquí van -si existen- los otros lugares
> donde se documenta información) ) Y definir / verificar si ya se
> cuenta con la manera correcta y / o formato idóneo para nuestro caso
> particular con el cual se documente cada cosa (el agente debe
> documentar la información correcta, en el sitio correcto, todas las
> veces; que cada registro documental salga del mismo molde ), así como
> también asegurar que la información que se documenta incluye
> exactamente cada detalle relevante y útil. Todo esto se debe hacer de
> la mano con las recomendaciones al respecto que se consulten ante las
> máximas fuentes de autoridad en la materia verificadas. Solo
> información verificada y actualizada utilizando web y Context 7 para
> confirmar. Es muy importante asegurar que todo se documenta siempre de
> la misma forma. El objetivo final es documentar la información
> correcta, en el lugar correcto y de la forma correcta todas las veces,
> en nuestro caso particular.
>
> 1.1) \[DOCUMENTACIÓN EN SECCIÓN “CITA POR DESICIÓN CON URL REAL” –
> RELACIONADA CON INCISOS 1.) Y 14.)\] q.) ¿Qué es exactamente lo que se
> documenta en la sección citas por decisión? w.) ¿acaso es un apartado
> que reúne los links a la evidencia que permitió concluir que una
> premisa era “confirmada” o “contradicha”? si la respuesta a la
> pregunta anterior es si y se usan links, e.) ¿cada link que se muestra
> está asociado únicamente al veredicto final que esa premisa tuvo? Si
> una premisa es ajustada n veces hasta ser finalmente confirmada o
> contradicha, r.) ¿el link asociado a cada veredicto que no es el final
> se muestra en esta lista? t.) ¿cada veredicto se emite siempre con
> base al mismo link (misma fuente)? Si la respuesta a la pregunta
> anterior es si, y.) ¿No tendría más sentido poder leer la evidencia
> textual de la fuente que leyó el agente y poder leer también el
> análisis sobre esa información que realizó el agente y que le permitió
> emitir el veredicto\*\*? o.) ¿El propósito originalmente pensado para
> esta sección es el de ir a ella a copy/pastear citas en la
> bibliografía de documentos académicos asociados a mi trabajo de grado?
> Responde q, w, e, r, t, o. y la responderás mas abajo cuando se te
> indique.

Mi principal prioridad no es solo tener links, sino tener mecanismos
idóneos y pertinentes en nuestro caso particular, que me permitan tener
total claridad de cuál fue el razonamiento del agente y con base en que
evidencia (web textual, ctx 7 textual, artifacts como el agents.md,
código fuente, etc) es que llegó a esos razonamientos con los que tomó
decisiones y/o emitió juicios sobre premisas o criterios, para que yo,
como humano, pueda auditar y aprobar o ajustar un plan sabiendo por qué
el agente llegó a las conclusiones que le hicieron tomar esas
determinadas decisiones, y si de hecho esa toma de decisiones tuvo
sentido o no para mí. Ello me da la capacidad de evaluar el plan que se
está por implementar recorriendo cada parte involucrada en su concepción
y refinamiento hasta el borrador que me entregan a mi para que lo
confirme o mande a ajustar.

Hablo de conocer que información per se (textual) el agente buscó en las
diferentes fuentes de consulta (aquellas fuentes “de autoridad en la
materia” encontradas en la web o a través de mcps como ctx 7, y aquellas
fuentes “externas”, como el código fuente, partes del borrador del plan,
otros ficheros en formato.md u otras) y como y bajo que razonamientos
suyos utilizó piezas de información provenientes de aquellas distintas
fuentes de consulta para contrastarlas y llegar a
conclusiones/razonamientos que sustentan la toma de determinada
decisión. P. ej., quisiera poder leer textualmente que renglones
provenientes de la fuente de autoridad en la materia consultada
(asumiendo que aplicó en el caso) son los que el agente interpretó y
contrastó frente a qué parte del plan y frente a qué parte del código
fuente y cuál fue el análisis que hizo bajo su criterio involucrando
todas esas fuentes de información (partes del plan, código fuente, otros
ficheros en formato.md, fuentes “de autoridad en la materia” si aplican)
para terminar por concluir que la premisa x fue confirmada o
contradicha.

Quiero saber y poder consultar cuál fue el análisis completo que hizo el
agente (contrastando evidencias provenientes de las distintas fuentes de
consulta) detrás de las decisiones fundamentales que se tomaron en la
hechura del plan que se me entrega para que lo revise y apruebe o ajuste
(incluyendo también aquellas decisiones aparentemente “inocuas” pero que
pueden ser las que esclarecen por qué todo está fallando). P. ej. Fuente
de autoridad en a materia A, apartado textual de la misma y análisis que
explica por qué esa información, al ser contrastada contra la evidencia
proveniente de la fuente externa “sección(es) en específico del borrador
del plan”, apunta a confirmar una premisa. P. ej. 2 Razonamiento inicial
del agente (lo que entendió que debía hacer), fuentes externas
consultadas (u evidencias exactas provenientes de otros tipos de fuentes
empleadas bajo razonamiento propio del agente), partes exactas de esas
fuentes externas y/o otras evidencias y análisis del agente sobre ellas
y sobre las partes del plan y/o el código fuente (si aplica) que explica
por qué se tomó determinada decisión / emisión de juicio frente a la
confirmación o contradicción de un criterio; Es decir, análisis que
explica por qué dichas fuentes externas (o por qué las evidencias que el
agente encontró bajo su razonamiento propio si no hay fuentes externas)
apuntan a que determinada parte del borrador del plan hace que este no
pueda encontrar “confirmado” o “contradicho” el criterio X de la
rúbrica. También es cierto que, si el propósito de esas citas por
decisión es para uso en bibliografías de informes académicos, no quiero
que el agente se lie al mezclar tareas de documentación de decisiones
que se tomaron mientras se construía el plan con tareas de entregar
links en formato apa para informes académicos, y que, por intentar hacer
tareas tan diferentes, no haga ninguna bien.

> Sin embargo, a.) lo que yo quisiera que el agente registre en la
> sección citas por decisión (ejemplos 1, 2), así como b.) las
> preocupaciones de mezclar tareas y también las c.) dudas sobre cuál es
> el verdadero propósito inicialmente dado a esta sección, y si dicho
> propósito inicial tiene sentido en nuestro caso particular o si tiene
> más sentido que en lugar de solo registrar links, se registre la
> información textual de las fuentes de autoridad en la materia y el
> análisis que hizo el agente interrelacionando esa información de las
> fuentes de autoridad con evidencias provenientes de distintas otras
> fuentes de consulta -o evidencias provenientes de fuentes ajenas a las
> “de autoridad en la materia” en caso que no haya fuente aplicable
> allí- que le permitió al agente tomar determinadas decisiones
> (confirmar / contradecir un criterio o premisa), son todas ellas
> cuestiones (a, b y c) que, una por una, es necesario saber que tiene
> más sentido hacer frente a ellas (aplicaras, descartarlas, o ¿existen
> otras recomendaciones pertinentes?) en nuestro caso particular,
> consulta información fiable y actualizada recogida ante las máximas
> fuentes de autoridad en la materia (ctx7 + web para confirmar) qué es
> lo que dicha información sugiere frente a todo esto, y qué confirma
> como lo correcto, óptimo y pertinente que podemos y/o deberíamos (o
> nó) hacer en nuestro caso particular y por qué. Al final de
> consultarlas y responder, responde la pregunta antecedida por el
> inciso y y también responde la pregunta: En esa lista de cistas por
> decisión, ¿citas sobre qué decisiones tomadas en donde se incluye?
>
> Adicionalmente, quedan 2 dudas.
>
> ¿Debería existir una sección “citas por decisión” específica para la
> información asociada a la confirmación o contradicción de premisas, y
> otra exclusiva para las decisiones asociadas a la graduación de la
> rúbrica (confirmación/contradicción de sus criterios)?
>
> ¿Cómo se deberían gestionar los espacios en blanco que quedarían en la
> sección citas por decisión para todas las decisiones para las cuales
> no hubo fuentes que aplicaran, de modo que son decisiones tomadas 100%
> bajo el criterio inspección análisis de la gente? Frente a estas 2
> últimas dudas confirmar con información fiable y actualizada recogida
> ante las máximas fuentes de autoridad en la materia (ctx7 + web para
> confirmar) qué es lo que dicha información sugiere frente a ellas y
> qué es lo que dice que es lo correcto, óptimo y pertinente que podemos
> y/o deberíamos (o nó) hacer en nuestro caso particular y por qué.
>
> \* \* Esta pregunta está directamente asociada con la propuesta de
> bitácora, y más concretamente con la propuesta de lo que debería
> registrar la sección “Resumen por Rondas” de la misma, propuesta que
> se encuentra detallada en el inciso numerado 14.)
>
> 1.1.2) \[DUDA COMPLEMENTARIA A 1.1 SOBRE SI EN VERDAD TIENE SENTIDO
> QUE EXISTA UNA SECCIÓN “CITAS POR DESICIÓN” - ACTUALIZADA\]
>
> 1.) Si va a existir un apartado en la sección “fuentes de autoridad”
> que detalle las citas por decisión, hay que tomar en consideración los
> diferentes tipos de fuentes de origen que existen para cada evidencia
> involucrada en la toma de decisiones; si se habla de decisiones sobre
> si un criterio es confirmado o contradicho, entonces tenemos como
> principal fuente de origen de las evidencias (que se utilizan para
> confirmar o contradecir una premisa) a las fuentes de “autoridad en la
> materia”, que son todos aquellos recursos disponibles a través de
> internet a través de la web (solo sitios web que cumplan con estos 3
> checks: link accesible y funcional, recurso verificado, y versión
> actualizada del recurso verificado consultado en el caso) o a través
> del mcp de context 7. Pero también existen otro tipo de fuentes;
> aquellas como ficheros.md o ficheros.py, e incluso otras que el agente
> utilice bajo su propio criterio cuando no haya fuentes de autoridad
> disponibles, las cuales también proporcionan evidencia que se puede
> llegar a utilizar para confirmar o contradecir una premisa dentro del
> inciso b del paso 6 del procedimiento numerado en plan-redactor.md.
> Ahora, si hablamos sobre las decisiones que se toman frente a los
> criterios de la rúbrica y si un plan los cumple o nó en la sección c
> del paso 6 del procedimiento numerado de plan-redactor.md, entonces
> también sucede que existen estos mismos tipos de fuente de donde
> provienen las evidencias. Y si los links que se detallan en cita por
> decisión solo existen para la toma de algunas decisiones y no todas
> -asumiendo que allí no se cita haciendo referencia a rutas a nivel de
> SO, sino solo con links cuando los hay- (que además son decisiones
> sobre si el plan sufrió modificaciones o nó en función de la
> confirmación o contradicción de sus premisas y criterios) Entonces me
> cuestiono ¿cuál la verdadera utilidad de las citas por decisión si ya
> existen las bitácoras? Puedo inferir que su propósito inicial era el
> de servirme a mí para nutrir mi bibliografía pero ahora me pregunto si
> en verdad vale la pena que ese apartado exista, o si solamente va a
> dar citas que representan información “a medias” sobre decisiones que
> involucraron el análisis a más fuentes que no se citan, mientras al
> mismo tiempo existe el riesgo que el agente empiece a alucinar o a
> agotar su ventana de contexto detallando información para la
> bibliografía de mis informes al tiempo que debe concentrarse en otro
> tipo de tareas no ligadas a la escritura académica. Debemos confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos y/o deberíamos (o nó)
> hacer en nuestro caso particular y por qué.
>
> 2.) \[DOCS, REGISTRO EN BITACORA\] Dejar indicado de forma explícita
> que en la bitácora solo se registra el desenlace de cada premisa, una
> fila = una premisa, con el matiz que bajo la columna Acciones
> Aprobadas se registra el desenlace para cada corrección a lo largo de
> cada iteración para esas premisas, con detalles relevantes + el bullet
> si es que hubo esas correcciones. Confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) si esto tiene sentido y si es lo
> más óptimo que podemos hacer en nuestro caso particular.
>
> 3.) \[PROCEDIMIENTO RÚBRICA\] En la rúbrica revisar si lo que más
> conviene es decirle que evalúe el plan o decirle que evalúe el plan
> por partes. Confirmar con información fiable y actualizada recogida
> ante las máximas fuentes de autoridad en la materia (ctx7 + web para
> confirmar) qué es lo óptimo que podemos hacer en nuestro caso
> particular.
>
> 3.1) \[DUDA COMPLEMENTARIA A 3.) SOBRE ESPECIFICIDAD DE INSTRUCCIONES
> Y SI VALE LA PENA QUE EL CRITERIO C2 INCLUYA INSTRUCCIONES EXPLÍCITAS
> ESPECÍFICAS DE COMPARAR EL PLAN CONTRA EL CÓDIGO FUENTE\] dentro de la
> rúbrica, en el criterio c2 se podría especificar de forma aún más
> explícita que aquello se contrasta contra 1, 2 y 3 es el plan.
> Adicionalmente, surge la duda: ¿En nuestro caso particular, ¿Valdría
> la pena que se incluya instrucciones explícitas que obliguen al agente
> a contrastar el plan contra 1, 2, 3 y el código fuente entero y/o las
> secciones que el plan señala a intervenir para poder tener absoluta
> certeza que el plan no introduce antipatrones? ¿Valdría la pena que el
> análisis que el agente utiliza para emitir juicio sobre el criterio,
> análisis que construye contrastando evidencias de distintas fuentes
> (el plan vs 1, 2 y 3 p. ej.) incluyera también al código fuente como
> evidencia?
>
> 3.1.1) \[DUDA COMPLEMENTARIA A 3.1 SOBRE SI VALE LA PENA PULIR CIERTOS
> DETALLES EN LA REDACCIÓN DE LA SECCIÓN C DEL PASO 6\] ¿Valdría la pena
> ajustar la redacción en el inciso c del paso 6 para que sea específico
> al decir “gradúa este plan parte por parte” en lugar de que
> simplemente diga “gradúa este plan”? confirmar con información fiable
> y actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 3.2) \[OBSERVACION Y DUDAS COMPLEMENTARIAS A 3.) SOBRE FALTA DE
> CLARIDAD AL INDICAR AL AGENTE CÓMO DEBE ITERAR SOBRE LOS CRITERIOS DE
> LA RÚBRICA AL GRADUARLA\] Contrario a como sucede con el caso de la
> confirmación o contradicción de las premisas, en el inciso c del paso
> 6 se evidencia ausencia total de instrucciones completas, claras y
> explícitas que le indiquen al agente exactamente cómo debe iterar
> sobre cada uno de los criterios de la rúbrica. Para ser más concretos,
> en c Hay ausencia completa de instrucciones explícitas que le indiquen
> al agente que no debe continuar a evaluar el siguiente criterio hasta
> que no resuelva la situación de cada criterio que encuentre
> inicialmente contradicho. Es solo hasta la sección d donde de forma
> implícita y algo ambigua se le intenta explicar al agente que si se
> encuentra con un criterio contradicho no debe avanzar a evaluar el
> siguiente criterio hasta refinar y ajustar el plan para confirmar
> aquel criterio inicialmente contradicho, similar a como sucede en el
> caso de la confirmación o contradicción de premisas. Tampoco se
> detalla de forma clara y explícita a que fuentes se esta haciendo
> referencia cuando se le dice al agente que debe “iterar si una fuente
> contradice”. ¿Acaso se hace referencia a las “fuentes externas”
> detalladas en C2? ¿A que fuentes se hace referencia? ¿vale la pena que
> la lógica de “no avanzar al siguiente hasta definir la situación del
> que tengo en frente -es decir, que el criterio se confirme o se
> descarte-” se aplique a la graduación de la rúbrica, así como
> actualmente se aplica a la confirmación / contradicción de criterios?
> frente a esto, es necesario confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 3.2.1) \[OBSERVACIÓN CRÍTICA COMPLENTARIA A 3 y 3.1 – AUSENCIA
> CONFIRMADA DE INSTRUCCIONES EXPLÍCITAS SOBRE QUE HACER EN CASO DE QUE
> UN CRITERIO NO PUEDA SER CONFIRMADO TRAS AGOTARSE EL MÁXIMO DE RONDAS
> DE CONFIRMACIÓN/CONTRADICCIÓN POR CRITERIO\] Actualmente no existen
> instrucciones claras para el agente sobre qué debe hacer en caso de
> que un criterio de la rúbrica no pueda ser confirmado una vez se agote
> el máximo de iteraciones por criterio durante la graduación de la
> rúbrica. En el caso de las premisas se dice que la premisa es
> descartada y si las fuentes de autoridad dan recomendaciones que están
> dentro del alcance del tag, estas se adoptan, de lo contrario, no se
> adoptan las recomendaciones y se registra la ocurrencia en la sección
> “Residuales” del plan. Sin embargo, en el caso de la graduación de la
> rúbrica no hay absolutamente ningunas instrucciones para el agente
> sobre qué hacer si determinado criterio sigue contradicho después del
> máximo de 2 rondas de refinamiento definido por criterio. Como no se
> le dice qué hacer, por lo tanto dependemos de su propia inferencia con
> base en su propio razonamiento y esto hay que corregirlo. Debemos
> confirmar con información fiable y actualizada recogida ante las
> máximas fuentes de autoridad en la materia (ctx7 + web para confirmar)
> qué es lo que dicha información sugiere frente a todo esto y qué es lo
> que dice que es lo correcto, óptimo y pertinente que podemos y/o
> deberíamos (o nó) hacer en nuestro caso particular y por qué.
>
> 3.3) \[DUDA COMPLEMENTARIA A 3.) Y RELACIONADA CON 1.), 3.2), 3.2.1),
> 4.) y 10.) SOBRE POR QUÉ LA RUBRICA SOLO INDICA REGISTRAR “EN EL
> DELTA” LAS MODIFICACIONES AL PLAN QUE SE REALICEN PARA QUE ESTE CUMPLA
> CON EL CRITERIO C2 \] Asumiendo que el propósito del delta es
> registrar los cambios que se realicen al plan cada vez que este sufra
> de ajustes para que pase a tener “confirmadas” afirmaciones validables
> inicialmente “contradichas” que pueden ser premisas (si es que el plan
> se está “validando” de acuerdo al inciso b del paso 6) o criterios (si
> se está contrastando contra los criterios de la rúbrica en el inciso c
> del paso 6)\*\* , surge la siguiente duda: ¿Por qué en las
> instrucciones de graduación de la rúbrica -paso 6, inciso c- solo se
> instruye en registrar en el delta las modificaciones al plan resultado
> de ajustes para que este cumpla con el criterio c2, en lugar de
> existir una instrucción clara, explícita y exacta que le indique al
> agente que debe registrar en el delta\*\*\* las modificaciones al plan
> resultado de ajustes en el mismo para tener “confirmado” cualquiera de
> los criterios de la rúbrica? Infiero que el delta asociado a
> información de la graduación de la rúbrica\*\*\* debe registrar todos
> los cambios al plan, y no solo aquellos vinculados al criterio C2.
> Debemos confirmar con información fiable y actualizada recogida ante
> las máximas fuentes de autoridad en la materia (ctx7 + web para
> confirmar) qué es lo que dicha información sugiere frente a todo esto
> y qué es lo que dice que es lo correcto, óptimo y pertinente que
> podemos y/o deberíamos (o nó) hacer en nuestro caso particular y por
> qué.
>
> \*\*Al hablar de cómo se gradúan los criterios de la rúbrica, se asume
> que los criterios de esta serán iterados de acuerdo con lo planteado
> y/o respondido en el inciso numerado 3.2) previamente respondido; se
> plantea en el -quedando pendiente consulta a su respuesta completa-
> que al graduar la rúbrica, no se avanza al siguiente criterio hasta
> tener el veredicto final de uno inicialmente contradicho; y ello
> inevitablemente se relaciona con lo respondido en el inciso numerado
> 3.2.1), referente a que hacer si dicho veredicto final es
> “contradicho”.
>
> \*\*\*Al hablar del registro en el delta, se hace referencia directa a
> lo planteado y/o respondido en el inciso numerado 4, acerca de la no
> existencia de un delta para información asociada a la graduación de la
> rúbrica.
>
> NOTA ADICIONAL: Este inciso (3.3) está relacionado con 1.) en tanto
> trata sobre documentación en el delta, pero también con el inciso 10.)
> -ver su respuesta completa si existe o preguntar por si ya tiene
> respuesta o no en caso de no encontrarla, no consultar en la web para
> este inciso sino preguntar si ya tiene respuesta si no la encuentras
> en el historial del chat- ya que este (el inciso 10.) y sus
> complementarios) plantea la necesidad de reglas que permitan que el
> borrador del plan que se entregará para revisión del humano (yo)
> después de los ajustes que sufra para tener confirmados los criterios
> y/o premisas, al final, siga reflejando en su totalidad cada una de
> las premisas “confirmadas” (las rechazadas nunca van al plan) y siga
> reflejando las evidencias que soportan cada criterio “confirmado” o
> “rechazado” -tomando en consideración los planteado y/o respondido en
> 3.2.1) sobre que hacer si un criterio se queda “contradicho” después
> de agotar la última ronda de iteración para la verificación de su
> cumplimiento-.
>
> 4.) \[ (RÚBRCA) REGISTRAR EN DELTA INEXISTENTE INFO QUE PARECIERA
> DEBER IR EN BITACORA NO EXISTENTE\] Hay un comportamiento bastante
> curioso y es que cuando el criterio c2 solamente puede ser evaluado y
> tener juicio emitido partiendo únicamente del razonamiento del agente
> junto con el análisis que haga al código fuente, se le está indicando
> actualmente que registre en el Delta la decisión como “pragmática sin
> respaldo” excepto que no existe tal Delta para el registro de
> información asociada a la graduación de criterios en la rúbrica,
> porque en la sección fuentes de autoridad solo se detalla un Delta con
> indicaciones referentes al proceso de confirmación / contradicción de
> premisas contra fuentes. Adicionalmente, pareciera que la intención
> fuera colocar esa información en la equivalencia al Delta de las
> premisas, pero para el procesamiento de los criterios; Excepto que,
> así como no existe una bitácora para registrar información asociada a
> la graduación de la rúbrica tampoco existe un Delta para registrar
> información asociada a ese mismo proceso de graduación de la rúbrica.
> ¿Deberían crearse la bitácora y el delta para el registro de
> información asociada a la graduación de la rúbrica? ¿Debería existir
> una sola bitácora y delta para ambos? ¿la bitácora debería encargarse
> de hacer el trabajo del delta? ¿se debería crear una bitácora
> universal para información asociada a la confirmación/contradicción de
> premisas y/o criterios de la rúbrica? confirmar con información fiable
> y actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 4.1) \[OBSERVACIÓN CRÍTICA Y COMPLEMENTARIA A 4.) - NO EXISTEN
> INSTRUCC\]
>
> 5.) \[DEFINIR “CONTROVERSIAL” Y ESCALRECER A DONDE EL AGENTE BUSCA
> ESAS DESICIONES\] Es necesario definir los criterios correctos para
> establecer qué decisiones son controversiales; en la rúbrica, el
> criterio cuatro (c4) le dice al agente que debe verificar que toda
> “decisión controversial” esté acompañada de cierta información,
> excepto que no hay un criterio que defina claramente que es lo que
> hace “controversial” a una decisión más allá el juicio que pueda
> emitir el propio agente partiendo de su razonamiento y del análisis de
> código y demás artefactos como el verificacion.md. Dentro de la
> información que se pide verificar que existe para las “decisiones
> controversiales”, están: justificación contraparte y cita real cuando
> existe y también que, si no hay fuente real, la decisión esté marcada
> como pragmática sin respaldo con justificación propia. Se exige que no
> haya citas inventadas. Hay que esclarecer si esta instrucción tiene la
> intención de que el comportamiento del agente sea ir a las bitácoras
> (asumiendo que las fuentes de autoridad consultadas hayan dictaminado
> que en nuestro caso particular tiene sentido y es necesario tener
> bitácora y delta asociados a la graduación de criterios en la rúbrica,
> así como existen para el confirmación / contradicción de criterios), Y
> es necesario consultar ante la información actualizada que provenga de
> las máximas fuentes de autoridad verificables y fiables (web y ctx 7
> para confirmar), Cuál es la forma correcta y óptima en nuestro caso
> particular de definir esos criterios para el agente sobre lo que es
> controversial o si ya es sobre ingeniería pero de nuevo basándonos en
> nuestro caso particular y en lo que dictamine la información
> consultada ante las fuentes.
>
> 6.) \[REDACCIÓN EXPLICITA DE A DONDE EL AGENTE DEBE IR A VERIFICAR
> URLS\] En el C 5 es pertinente aclararle al agente a dónde exactamente
> deberá buscar esas url que tiene que verificar que superen los 3
> checks del punto B. Se puede inferir que el comportamiento deseado es
> que revise cada bitácora cada cita sin embargo esa es una inferencia
> mía porque realmente no queda explícitamente definido a dónde tiene
> que ir a verificar esas URLS.
>
> 7.) \[(RÚBRICA) – ACLARAR INSTRUCCIONES ACERCA DE ITERACIÓN SOBRE
> CRITERIOS E INSTRUCCIONES CUANDO UNO NO PUEDE SER CONFIRMADO\] En el
> paso 6 en el apéndice d, a pesar de que al agente se le dice que
> “Itera: si la rúbrica falla o una fuente contradice, refina y
> re-evalúa. Máximo 2 rondas de refinamiento.”, Yo me cuestiono si al
> agente le queda claro cuál es el comportamiento que debe asumir y que
> debe hacer en caso de que se encuentre por primera vez con un criterio
> que no puede ser confirmado; ¿acaso debería reiterar para corregir las
> partes del plan que hacen que ese criterio no pudiera confirmarse y no
> avanzar a evaluar contra el siguiente criterio hasta ajustar el plan y
> que se pueda confirmar el criterio inicialmente contradicho? (similar
> a como sucede con el procedimiento de las premisas), O ¿acaso debería
> empezar a barrer cada criterio nuevamente de arriba abajo desde cero?
> También se identifica que al agente no se le proporcionan
> instrucciones claras sobre qué debe hacer en caso de que un criterio
> no pueda ser confirmado después de las oportunidades máximas de ajuste
> por criterio. (en el caso particular de las premisas, la premisa es
> descartada, y como particularidad única de ese caso, si las
> recomendaciones de las fuentes están dentro del alcance, se
> implementan y si no, se dejan anotadas en “residuales” como trabajo
> futuro). Es necesario y debes confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo más óptimo que podemos
> hacer en nuestro caso particular (que se detenga en cada criterio
> contradicho para ajustar y que pase a ser confirmado y ahí si continue
> a evaluar el siguiente, o iterar la rúbrica completa u otra
> recomendación pertinente y óptima en NCP), y, cuáles son las
> instrucciones correctas, óptimas y pertinentes en nuestro caso
> particular para indicarle al agente que debe hacer si un determinado
> criterio no logra confirmarse aún después de agotar el máximo de
> oportunidades de ajuste.
>
> 7.1) \[COMPORTAMIENTO DEL AGENTE Y ¿A QUÉ FUENTES SE HACE REFERENCIA
> EN LA SECCIÓN “D” DEL PASO 6?\] yo me cuestiono si hay la suficiente
> claridad sobre qué quiere decir que una fuente “contradiga” y también
> me cuestiono si tiene sentido que el agente verifique si esas fuentes
> contradicen y a dónde debería ir el agente a buscar esas fuentes en
> primer lugar. Si las fuentes nacen con el propósito de confirmar o
> contradecir premisas en la sección b, y en el caso de la rúbrica, con
> el propósito de servir como fuente de comparación para emitir juicios
> en el criterio C2, ¿por qué el agente debería ir a revisar nuevamente
> las citas asociadas a alguno de estos 2 procedimientos y/o partes del
> paso 6? ¿Eso tiene sentido? En el caso del procedimiento de
> confirmación o contradicción de las premisas si una premisa es
> contradicha por las fuentes tiene dos oportunidades adicionales para
> ser ajustada hasta que las fuentes dejen de contradecirla. Sin
> embargo, si al final de esas dos oportunidades la premisa sigue
> contradicha se descarta y eso quiere decir que van a haber escenarios
> en donde la bitácora de las premisas va a contener fuentes Que
> contradijeron 3 veces determinada premisa que resultó descartada. Si
> el agente revisa esa fuente, y revisa lo que originalmente asumía la
> premisa, y confirma lo ya confirmado (que la fuente contradice la
> premisa), ¿acaso va a hacer que ese criterio de la rúbrica falle? ¿o
> es que acaso se está haciendo referencia a las fuentes de C2? Porque
> También se podría inferir que hace referencia a que una fuente del
> criterio C2 “contradiga” sin embargo, si una fuente del criterio dos
> contradice pues la rúbrica falla y no hay claridad sobre si la rúbrica
> debería seguirse evaluando (es decir, si en C2 “contradice”, seguir
> con C3.. C4 etc) o si en ese momento debería empezar la segunda
> iteración de verificación sobre el criterio C2, o si debería volver a
> iterar desde 0 de arriba a abajo los criterios de la rúbrica, pero
> entonces C3, C4 Y C5 no serían revisados durante el primer barrido si
> el criterio C2 presenta o posee una “fuente que contradice”. Confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) que sugieren
> frente a todo esto y qué es lo que dicen que es lo óptimo que podemos
> hacer en nuestro caso particular.
>
> 7.2) \[DUDA COMPLEMENTARIA DE 7 SOBRE \]
>
> 8.) \[DUDAS SOBRE LAS REGLAS DE DOCUMENTACIÓN EN LA BITÁCORA DE LAS
> PREMISAS (Y DE LOS CRITERIOS, SI LAS FUENTES AVALARON SU CREACIÓN DE
> ACUERDO AL PUNTO 4)\] ¿Bajo qué reglas el agente va actualizando la
> bitácora de las premisas a medida que avanza iterando sobre cada
> premisa? ¿si estamos definiéndole esas reglas claras y si son las
> adecuadas en nuestro caso particular? ¿el lugar donde se ubican esas
> reglas (si es que existen como tal) es el adecuado? ¿Qué
> recomendaciones emiten frente a todo esto las máximas fuentes de
> autoridad en la materia? Confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) que sugieren frente a todo esto y
> qué es lo que dicen que es lo óptimo que podemos hacer en nuestro caso
> particular. DUDA ADICIONAL: si en el punto (4) las fuentes avalaron la
> creación de la bitácora de información asociada a criterios, entonces,
> ¿Qué respuesta hay a todas estas preguntas en el caso de el registro
> de información de los criterios?
>
> 9.) \[DUDA DE BAJA PRIORIDAD POR CONFIRMAR\]Una premisa descartada,
> independientemente de si las recomendaciones de la fuente entran en el
> alcance del tag o no, ¿queda registrada en el Delta? R./ -\> si,
> DEBERÍA. (según yo, pregunto solo porque es mejor confirmar).
>
> 10.) \[FALTA DE CLARIDAD SOBRE REGLAS QUE IMPIDAN LA MODIFICACION
> SOBRE PARTES DEL PLAN ASOCIADAS A PREMISAS / CRITERIOS YA
> CONFIRMADOS\] ¿Es posible que un agente arruine y o modifique
> secciones del plan asociadas a una premisa o criterio previamente ya
> confirmados al intentar corregir una premisa o criterio que encuentre
> contradichos? Hay 3 escenarios que se deben evitar: 1: al ajustar
> partes del plan para intentar que una premisa B contradicha cambie y
> pase a ser confirmada, el alcance en esos ajustes a determinadas
> partes del plan se solapa con partes del plan asociadas a premisas
> previamente confirmadas, como la premisa A, de manera que ocurren
> modificaciones que hacen que la premisa A, previamente confirmada,
> deje de ser reflejo fiel de las partes del plan que afecta (hasta
> podría suceder que si se construyera una premisa nueva con base en las
> partes del plan que pertenecían a la premisa A pero que sufrieron
> modificaciones en intentos de ajustar la premisa B, esa nueva premisa
> no sea correcta, pertinente, óptima ni confirmable ante fuentes). 2:
> al ajustar partes del plan para intentar que se cumpla y/o confirme un
> criterio B de la rúbrica inicialmente contradicho, el alcance en esos
> ajustes a determinadas partes del plan se solapa con partes del plan
> previamente revisadas durante la emisión del juicio de criterios que
> recibieron veredicto confirmado y/o satisfactorio, como el criterio A,
> de manera que ocurren modificaciones que hacen que el juicio emitido
> sobre el criterio A pase a ser un juicio que ya no es garantía de que
> el plan cumple con el criterio A porque desconoce las modificaciones
> en las que se incurrió al ajustarse el plan para cumplir con B y estas
> podrían, en algunos casos, hacer que el plan de hecho deje de cumplir
> en parte o en su totalidad con el criterio A\*\* (es decir, el
> veredicto emitido sobre A deja de ser reflejo de evidencias que lo
> soporten, y por tanto, pasa a entrar a “tela de juicio”). 3: al
> ajustar partes del plan para intentar que se cumpla y/o confirme un
> criterio X de la rúbrica inicialmente contradicho, se incurre en
> modificaciones en partes del plan inicialmente afectadas o
> “representadas” por la premisa Y, de manera que la premisa Y deja de
> ser reflejo fiel de las partes del plan que afecta. Esto es un
> problema porque al revisar la bitácora, podría suceder que se informe
> sobre premisas que son falaces y que no son realmente sobre las que se
> constituye la versión final y ajustada del plan. ¿Qué mecanismos se
> implementan para evitar que todo esto ocurra? de existir esos
> mecanismos ¿sí son los adecuados en nuestro caso particular? ¿si los
> entiende bien el agente todas las veces (asumiendo que el agente build
> es quien invoca al sub-agente plan-redactor)? dichos mecanismos, (si
> existen), ¿se ubican en donde deberían ubicarse? ¿Los 3 escenarios se
> evitan creando reglas para delimitar el alcance de las modificaciones?
> ¿Qué debería hacer el agente si al evaluar el alcance de las
> modificaciones para ajustar determinada premisa o criterio, se
> determina que este (el alcance) se solapa con partes del plan
> asociadas con premisas y/o criterios previamente confirmados? ¿Cuál es
> la forma correcta de hacer que el agente sepa que esta por tocar
> partes del plan que ya hacen de un criterio y/o premisa “confirmado”?
> esto último, ¿tiene sentido? Frente a todo esto, ¿qué recomendaciones
> emiten las máximas fuentes de autoridad? Confirmar con información
> fiable y actualizada recogida ante las máximas fuentes de autoridad en
> la materia (ctx7 + web para confirmar) que es lo que esa información
> de las fuentes sugiere frente a todo esto y qué es lo que dicen que es
> lo correcto, óptimo y pertinente que podemos hacer en nuestro caso
> particular. \*\*\*
>
> \*\* En este planteamiento asume -contando con que previa consulta y
> aval ante las fuentes- que la rúbrica no avanzara al siguiente
> criterio hasta definir la situación de uno contradicho; entonces las
> modificaciones para ajustar y cumplir con B solo pueden afectar a A si
> y solo si A fue “confirmado” previamente.

\*\*\* Al final, hay una “NOTA:”. Su contenido es extenso y mientras
redactaba 10.) caí en la cuenta del análisis al que llegué mientras
pensaba sobre los 3 escenarios a evitar, dicho análisis resume el
propósito fundamental del flujo agentico.

> 10.1) \[DUDA COMPLEMENTARIA A 10.) SOBRE COMO GESTIONAR ADECUADAMENTE
> EL ESCENARIO EN EL QUE UNA PREMISA INICIALMENTE CONTRADICHA NO PUEDA
> SER AJUSTADA PARA SER CONFIRMADA DEBIDO A LIMITACIONES INTRODUCIDAS
> POR LAS REGLAS PRODUCTO DE LA RESPUESTA DE 10.)\] ¿Qué tan probable es
> que el plan no se pueda ajustar para que una premisa inicialmente
> contradicha C pase a ser confirmada, debido a que las modificaciones
> necesarias al plan para tal propósito sean impedidas por acción de
> reglas que se desprendan de lo concluido en 10.), las cuales estén
> entrando en acción para proteger las partes del plan que son reflejo
> de otras premisas A, B con estatus definitivo
> (confirmadas/contradichas) ya definido? Adicionalmente, ¿Cuál es la
> forma correcta, en nuestro caso particular, de que esas reglas que se
> desprendan de 10 hagan su trabajo de forma correcta y eviten llenar la
> bitácora de premisas que no reflejan el plan una vez este superó el
> inciso b del paso 6, pero sin impedir que premisas inicialmente
> contradichas puedan reformularse y el plan ajustarse de acuerdo con
> ellas? ¿acaso el agente debería ser instruido en iterar una vez
> adicional (después de que cada premisa haya agotado su máximo de
> rondas) de forma lineal sobre cada premisa para validar que cada una
> de ellas (incluyendo las que hayan sido reformuladas y el plan
> reajustado en consecuencia) sigue estando reflejada en la totalidad
> del plan? O ¿acaso es más conveniente que cada vez que el agente
> ajuste el plan para hacer que una premisa sea confirmada este se
> devuelva a confirmar que las premisas anteriores que hayan gastado su
> máximo de rondas de ajuste y por tanto ya tengan veredicto final
> (confirmadas / contradichas) sigan estando reflejadas en la totalidad
> del plan (esto no aplicaría obviamente a las premisas con estado final
> “contradichas” y por tanto “descartadas”)? ¿Existe una alternativa a
> parte de estas 2 que sea la más adecuada para permitir que cada grupo
> de instrucciones (de refinar cada premisa hasta ser confirmada o
> descartada y de asegurar que modificaciones al plan para confirmar una
> premisa inicialmente contradicha no resulten en que premisas
> anteriormente confirmadas dejen de estar reflejadas en todo el plan)
> funcione de forma correcta, óptima, eficiente y efectiva pero sin
> colisionar entre sí en nuestro caso particular? Debemos confirmar con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto, frente a cada una de las
> dudas que he planteado, y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 10.2) \[OBSERVACIÓN Y DUDAS COMPLEMENTARIAS A 10.) SOBRE CÓMO
> GESTIONAR ADECUADAMENTE EL ESCENARIO EN QUE DEBIDO A LA DEFINICIÓN DE
> LAS REGLAS INTRODUCIDAS EN 10.), NO SE PUEDAN REALIZAR LOS AJUSTES QUE
> SE NECESITARÍAN PARA CORREJIR LAS PARTES DEL PLAN QUE NO PERMITEN
> ENCONTRAR “CONFIRMADO” DETERMINADO CRITERIO\] ¿Qué tan posible es que
> determinado criterio de la rúbrica nunca pueda ser confirmado debido a
> que los ajustes que habrían que realizarse en determinada(s) parte(s)
> del plan para cumplir con dicho criterio no confirmado no pueda(n)
> realizarse debido a las reglas definidas tras la respuesta de 10.)
> -aquellas que evitan que por ajustar el plan para confirmar un
> criterio, se termine por “poner en entredicho” el cumplimiento de
> otros criterios previamente “confirmados”- ? ¿Cómo se debe gestionar
> de forma correcta en nuestro caso particular la situación para que
> aquellas reglas hagan bien su trabajo, pero no impidan que se ajuste
> el plan para que determinados criterios puedan llegar a ser
> confirmados? ¿sería necesario y/o óptimo decirle al agente que cada
> vez que ajuste el plan para cumplir con determinado criterio, se
> “devuelva” y verifique que los criterios anteriores que hayan sido
> superados aún siguen estando “confirmados”? ¿o acaso se debería
> agregar una cuarta iteración lineal sobre cada criterio para
> corroborar que, aún si se hicieron ajustes al plan para poder
> confirmar determinado criterio, cada veredicto emitido sigue siendo
> reflejo de evidencias que los soporten? Debemos confirmar con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos y/o deberíamos (o nó)
> hacer en nuestro caso particular y por qué.
>
> 11.) \[DUDA DE BAJA PRIORIDAD\] ¿valdría la pena que en la bitácora se
> incluyera la lista per se de cada premisa (afirmación validable)
> extraída directamente del borrador inicial del plan? (el borrador
> inicial es el que se construye justo después que el agente lee el
> análisis del verificador, y confirma el mapa completo de ficheros que
> sufren de la deuda técnica) ¿qué dicen las máximas fuentes de
> autoridad en la materia? Confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos hacer en nuestro caso particular.
>
> 12.) \[DUDAS SOBRE LA CORRECTA DELEGACIÓN DE TRABAJO EN EL FLUJO
> AGÉNTICO; ¿CÓMO HACER TODO LO QUE SE DEBE HACER EVITANDO LAS
> HALUCIONACIONES, SIMPLIFICACIONES E INCONVENIENTES POR
> AGOTAMIENTO/SUCIEDAD DE LA VENTANA DE CONTEXTO?\] ¿Qué tan capaz es un
> agente que esté siguiendo las instrucciones de plan-redactor de hacer
> un trabajo lo más libre de alucinaciones y / o simplificaciones
> posible que permita la creación de un plan.md correcto, completo y que
> resuelve bajo el alcance adecuado y de la forma adecuada la deuda
> técnica? La pregunta nace al considerar que el agente que lee
> plan-redactor debe absorber artefactos (verificacion.md), formular el
> borrador “0” del plan analizar el plan, abstraer de él las premisas
> pertinentes y validables, contradecir o confirmar esas premisas a
> veces con base en criterio propio (junto con la inspección del código
> fuente) y a veces con base en la retroalimentación de las fuentes
> consultadas, ir al plan y corregirlo en función de las premisas
> corregidas, ir documentando todo en la bitácora a medida que se
> analiza cada premisa, también ir documentando en delta cuando haya
> correcciones al plan y en residuales cuando aplique, armar el borrador
> “1” del plan con base en la corrección a premisas y partes afectadas
> por ellas, luego graduar ese borrador “1” contra la rúbrica, lo que
> implica confirmar o contradecir los criterios con base en lo que el
> plan propone + el contexto del proyecto, revisar agents.md y otras
> fuentes externas, a veces tomar decisiones 100% basado en criterio
> propio y análisis del código fuente, corregir el plan si incumple con
> determinados criterios hasta que cumpla con todos ellos, documentar
> nuevamente de la forma que se indique (bitácora, residuales, delta),
> aplicar mecanismos para evitar escenarios no deseados, etc.
> Considerando esto, surge una duda: ¿el flujo agéntico sí delega la
> totalidad del trabajo de forma que los agentes como build y subagentes
> invocados en el flujo puedan hacer un trabajo lo más libre de
> alucinaciones, simplificaciones y demás dificultades en la capacidad
> de hacer bien su trabajo asociadas al agotamiento de la ventana de
> contexto? frente a todo esto, ¿qué sugieren las máximas fuentes de
> autoridad en la materia de acuerdo a nuestro caso particular para
> favorecer el desempeño óptimo y libre de alucinaciones,
> simplificaciones y falta de ventana de contexto por parte de los
> agentes y/o subagentes involucrados? Confirmar con información fiable
> y actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos hacer en nuestro caso particular.
>
> 13.) \[DUDAS SOBRE MECANISMOS PARA GARANTIZAR LA CORRECTA CONSTRUCCIÓN
> DE PREMISAS\]¿Cuáles mecanismos específicos existen para garantizar
> que las afirmaciones validables que se extraen del borrador cero del
> plan son relevantes, pertinentes, Y reflejo fiel de la Constitución de
> ese primer borrador inicial del plan? ¿Si existen esos mecanismos? ¿En
> nuestro caso particular qué deberían hacer en donde deberían estar
> ubicados y cuál es la mejor forma o la forma correcta y óptima de
> hacer lo que deben hacer? Si no existen, ¿Qué mecanismos deberíamos
> emplear en nuestro caso particular? ¿en dónde los deberíamos ubicar? y
> ¿cómo hacer que hagan lo que deben hacer? Confirmar con información
> fiable y actualizada recogida ante las máximas fuentes de autoridad en
> la materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos hacer en nuestro caso particular.
>
> 13.1) \[DUDAS SOBRE MECANISMO PROCESO DE BÚSQUEDA DE INFORMACIÓN Y
> POSTERIOR CONTRADICCIÓN/CONFIRMACIÓN DE PREMISAS\] Actualmente el
> mecanismo que existe para que los agentes confirmen o contradigan un
> criterio se fundamenta en el uso de afirmaciones validables en
> conjunto con instrucciones de verificación para las mismas. Es decir,
> se le dice de forma explícita al agente (en el fichero
> plan-redactor.md) que debe utilizar esas afirmaciones validables para
> acudir a las fuentes de información pertinentes y validarlas de
> acuerdo con lo que esas fuentes dicen. Como se trata de afirmaciones
> validables, se parte de la premisa que decirle a la IA explícitamente
> que “confirme” lo que sostienen esas afirmaciones basta para que de
> hecho averigüe en fuentes idóneas si la respuesta a esas afirmaciones
> es “SI” o “NO” (a veces no hay fuentes útiles y se depende de su
> propio criterio + inspección del código) y ese es el mecanismo que
> actualmente empleamos para garantizar que la IA (el agente) haga bien
> su trabajo de validar esas premisas. Sin embargo, la pregunta es:
> según las máximas fuentes de autoridad en la materia, ¿ese mecanismo
> si es suficiente para asegurar que el agente haga bien su trabajo y de
> buenos resultados? ¿Ese mecanismo es suficiente para que sepa buscar
> las fuentes de información que verdaderamente sean útiles para
> confirmar o contradecir las premisas, y que además sepan contradecir o
> confirmar las premisas de forma correcta todas las veces? Confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos hacer en nuestro caso
> particular.
>
> 14.) \[DUDA QUE SE DESPRENDE DE LO COMENTADO EN 1.) – DOCUMENTACIÓN DE
> EVIDENCIAS DETRÁS DEL JUCICIO DE LAS AFIRMACIONES VALIDABLES (PREMISAS
> Y CRITERIOS)\] Al hablar de las evidencias (de distintas fuentes) y
> los razonamientos al respecto de dichas evidencias que el agente
> utiliza para confirmar o contradecir una premisa o criterio de la
> rúbrica, ¿esas evidencias y los análisis que el agente hace con base
> en ellas se están registrando? ¿cuál es la forma en que actualmente se
> registran esas evidencias y/o razonamientos y en dónde? en nuestro
> caso particular, ¿tiene sentido almacenar esa información? ¿qué
> sugieren las máximas fuentes de autoridad frente a todo esto? ¿cuál
> sería la forma correcta de hacerlo en nuestro caso particular?
> Hablando por ejemplo de la bitácora que registra información asociada
> a las premisas, actualmente se maneja de tal forma que una fila es un
> criterio de la rúbrica y el inicio de la fila detalla el desenlace (si
> se cumple o no el criterio tras el fin de las iteraciones). Luego
> aparece una sección donde se cita la fuente. Seguida a la fuente, la
> sección “Acciones Aplicadas” incluye una especie de registro de lo
> corregido en cada ronda para cada fila o premisa (si es que la premisa
> fue inicialmente contradicha y necesitó de ajustes).

Flujo documental para la bitácora de las premisas

Con relación al registro de información en la bitácora de las premisas,
(y/o criterios), y con relación a las evidencias que permitieron emitir
determinado juicio sobre premisas (y/o criterios), quisiera confirmar
con las fuentes sí tiene sentido que, por ejemplo, la bitácora de las
premisas pasara a registrar (para el desenlace solamente, es decir, para
la última “ronda” de esa premisa) 0.) el número de la premisa “#”, 1.)
la premisa per se (es decir, la afirmación validable y su texto exacto;
p. ej. “el cielo es azul”), 2.) el veredicto; confirmada o contradicha,
3.) la ubicación de la evidencia que lo sustenta. Más concretamente, 3
niveles de “ubicación; “el grueso,” la “parte específica del grueso” y
los links -caso de las fuentes de autoridad- o rutas a nivel de SO-caso
de las fuentes externas como fichero.md, fichero.py u otras si hubiere,
para cada una de las evidencias involucradas en el proceso de contraste
y análisis que condujo al veredicto final de la premisa.

Aclaraciones sobre 3.)

Origen de las evidencias.

Las evidencias pueden existir y provenir desde los siguientes tipos de
fuentes que se detallan a continuación:

> • plan.md
>
> • “fuentes externas” (ubicables mediante ruta del fichero como el
> código fuente -p. ej. c/user/fichero.py-, ficheros y/o artefactos
> terminados en .md -p. ej. c/user/artefacto.md, u otras no
> especificadas)
>
> • “fuentes de autoridad” (consultables a través de context 7 y/o en la
> web; como artículos, libros, documentación oficial, casuística
> documental seria, etc) que son ubicables con enlace -link- o lo que
> aplique en el caso de información consultada a través de ctx 7
>
> 3 Niveles de Ubicación de la evidencia (por cada evidencia)
>
> La ubicación de la evidencia proveniente de las fuentes ya detalladas
> se presenta en 3 niveles:
>
> • Nivel 1 -\> “El grueso”: Es la pieza de información completa donde
> existe la evidencia. Es el “grueso” de la información, como un
> artículo completo proveniente de web y/o ctx 7, o si es fuente
> “externa”, sección entera del artefacto, código fuente, u otro.
>
> • Nivel 2 -\> “Parte o partes especifica(s) dentro del grueso”: Es el
> lugar -o los lugares- específicos dentro de esa pieza completa de
> información -el grueso- en donde está la evidencia exacta per se. (p.
> ej. si hablamos de evidencia dentro de un artículo entero, fichero.md
> entero o fichero.py entero, aquellos serían el “grueso”, y dentro de
> ellos, existen las secciones que contienen la evidencia exacta; en el
> caso del artículo, en algún párrafo o párrafos suyos existirán las
> oraciones que contienen evidencia utilizada en el análisis detrás del
> cual se emitió un veredicto; y lo mismo sucede con los ficheros; en
> alguna sección específica del fichero.md y/o del fichero.py existe la
> evidencia per se utilizada en el análisis detrás del veredicto. A esos
> lugares específicos donde existe la evidencia es que se refiere el
> nivel 2.)
>
> • Nivel 3 -\> “La ruta que lleva a la información”: Son los links (en
> el caso de las evidencias provenientes de fuentes de autoridad) y/o
> rutas a nivel de SO (en el caso de las fuentes externas como
> fichero.md, fichero.py, otras no especificadas y el plan) detrás de
> los que vive “el grueso” que contiene la evidencia.

Fin de las aclaraciones sobre 3.)

Retomando sobre la propuesta de los ítems de información que deberían
registrarse en la bitácora, para su desenlace, (es decir, para el
“snapshot” de la premisa una vez llega a su veredicto final; “final”
quiere decir que es el veredicto que se obtuvo hasta que la premisa se
confirmó o hasta que se le agotó su máximo de rondas de ajuste:
confirmada y/o contradicha y por tanto descartada) están los incisos:

> • 4.): Análisis que involucra y detalla el correcto contraste entre la
> totalidad de las evidencias y como exactamente es que aquel contraste
> condujo a concluir determinado veredicto para la premisa y/o criterio
>
> • 5.) (si aplica): Estrategia de implementación de ajustes al borrador
> del plan en función de la premisa reformulada que fue confirmada (el
> borrador del plan es el borrador del plan que elabora plan-redactor,
> mismo del que se extraen las premisas).
>
> • 6.) (si aplica): Handoff que detalla con exactitud y completitud los
> ajustes planificados a realizar en el plan de acuerdo a 5.) vs los
> ajustes de hecho realizados al plan.
>
> • 7.) (si aplica): Diff que permite contrastar el texto exacto de la
> premisa per se inicialmente contradicha vs el texto exacto per se de
> la premisa reformulada y confirmada, y que también permite contrastar
> textualmente las partes del plan y como estaban en el momento “0” de
> acuerdo con la premisa per se inicialmente contradicha (que decían
> textualmente esas partes afectadas por la premisa contradicha, y en
> donde decían eso dentro del plan completo) vs las partes del plan
> afectadas por la premisa y como quedaron tras ser ajustadas para que
> reflejaran la premisa reformulada y confirmada (que quedaron diciendo
> esas partes del plan textualmente y en donde dentro del mismo plan).

Consideraciones generales sobre cada inciso numerado de información
propuesto para el registro del desenlace de la premisa en la rúbrica:

Todos los incisos numerados recién mencionados son solo descripciones de
lo que se quiere que quede registrado en la bitácora, pero dicho proceso
de documentación, para que llegara a ocurrir de esta forma -si fuentes
avalan- puede implicar ajustes en el inciso b del paso 6, para que allí
existan las instrucciones que permitan registrar la información correcta
y de la manera ya detallada por cada inciso numerado en la bitácora.

Bajo esta propuesta, cada registro en la bitácora (cada fila) equivale a
una premisa. Por cada registro en la bitácora, habría 9 “columnas” en
total; el número de la premisa, seguido de una columna para cada uno de
los 7 incisos numerados, y la columna “Resumen Por Ronda”. Los 7 incisos
numerados contendrían información únicamente de la última ronda de
ajuste posible para determinada premisa inicialmente contradicha - de
acuerdo con el inciso b del paso 6- por lo que se dice que representan
el “desenlace” de la misma. Por su parte, las premisas que no requieran
ajuste alguno para ser confirmadas o que tras ajustarce el máximo
posible de veces continúen “contradichas” tendrán representado su
“desenlace” únicamente en los incisos numerados 1 al 4.

> Consideraciones específicas sobre 5.), 6.) y 7.):

Las modificaciones al plan presumiblemente se hacen solo si la premisa
fue “confirmada”; mientras una premisa se reformule y no reciba
veredicto “confirmada”, o no requiera ser reformulada en primer lugar,
el plan no debería ajustarse\*\* y por tanto 4.) 5.) y 6.) no se
registrarían.

> 5.), 6.) y 7.) únicamente se registran en la bitácora cuando una
> premisa inicialmente contradicha, tras ser reformulada, logra obtener
> el veredicto de “confirmada”. Si tras agotar su máximo de rondas de
> ajuste, la premisa continúa obteniendo veredicto “contradicha”, esta
> será descartada, no se incluirá en el plan y sencillamente no hay
> razón para que en el inciso b del paso 6 se formule una estrategia de
> implementación que se implemente y produzca un diff y por tanto 5.)
> 6.) y 7.) no se registrarían en este escenario. No obstante, existiría
> evidencia desde 3 niveles distintos y su respectivo análisis que
> sustente el por qué del veredicto. Si la premisa no requiere de
> ninguna reformulación o ajuste para ser confirmada, es decir, en su
> primera ronda obtiene el veredicto de “confirmada”, entonces a nivel
> de incisos numerados que se registrarían en la bitácora ocurriría lo
> mismo que en el escenario anterior; solo habría registro de 1.), 2.),
> 3.) y 4.). En este escenario, también habría evidencia multinivel
> acompañada del análisis que sustenta el veredicto.

Propuesta Columna “Resumen Por Ronda”

La propuesta específica para lo que se debería registrar en la columna
“Resumen por ronda” -Anteriormente llamada “Acciones Aplicadas”- que se
describe a continuación debe confirmarse como una propuesta correcta,
óptima y pertinente en nuestro caso particular ante información fiable y
actualizada proveniente de las máximas fuentes de autoridad en la
materia (web + ctx 7 para confirmar) antes de ser implementada y por
tanto puede sufrir modificaciones más adelante.

Dicho eso, propongo que la columna “Resumen Por Ronda” tenga como
propósito llevar un historial documental liviano pero útil para entender
cuál fue la evolución de una premisa hasta su veredicto final
(confirmada o contradicha y por tanto descartada). Debo aclarar que
realicé un análisis de las piezas de información que se deberían incluir
en cada ronda independientemente del veredicto de la premisa, así como
la cantidad de registros que debería haber en función de si la premisa
es inicialmente contradicha - rama “veredicto es contradicha”- o no –
rama “veredicto es confirmada”-. Si ocurre la rama “veredicto es
confirmada” solo habría 1 registro en “Acciones Aplicadas”, si ocurre la
rama “veredicto es contradicha” entonces transcurrirá al menos una ronda
adicional de ajuste para la premisa, y tanto si ese es el caso o si
ocurren más rondas de ajuste para esa premisa inicialmente contradicha,
la columna “Acciones Realizadas” detallará siempre 4 piezas de
información; el texto exacto de la premisa en cada ronda -irá
evolucionando en función de su ajuste-, su veredicto, la ubicación de la
evidencia y el análisis que explica el veredicto por cada ronda.

Flujo documental de la columna “Resumen por Ronda”

Bajo esta propuesta, la columna “Resumen por Ronda” - - lleva registro
de las 4 piezas de información descritas bajo los incisos numerados 1.),
2.), 3) y 4.) de la siguiente manera:

> • Si fue una premisa que no necesitó de ajustes, -rama veredicto es
> confirmada- que en “Resumen por Ronda” se registre:
>
> 1.) La premisa per se (escrita tal cual + partes/secciones del plan
> que afecta.
>
> 2.) el veredicto -esto redundaría un poco con el desenlace que se
> muestra en la tercer columna del registro de la premisa en la
> bitácora, aunque solo sería así para la ronda donde se devele el
> veredicto final de la premisa (se confirme o quede rechazada); si la
> premisa sufrió, por ejemplo, de 2 reformulaciones hasta finalmente ser
> “confirmada”, en la columna “Resumen por ronda” se registraría
> información adicional a la del “desenlace”, la cual no redundaría con
> las demás columnas del registro-
>
> 3.) la ubicación de la evidencia. Aquí se distinguen 2 fuentes de
> origen de la evidencia; aquella proveniente de fuentes “de autoridad”
> (como apartes de texto extraídos directamente de la fuente web y/o
> fuente de ctx 7, ubicable con link y citable), aquellas provenientes
> de fuentes “externas” (ubicables con ruta a nivel de SO, se trata de
> artefactos.md, ficheros.py u otras sin especificar) o el plan. A
> diferencia del registro del desenlace de la premisa, que cuenta con
> ubicación multinivel de la evidencia, como esta columna es una fuente
> documental “ligera” que además detalla información asociada a todas
> las rondas de ajuste que presente la premisa, se omitirá la inclusión
> de la ubicación del “grueso” de la evidencia, permaneciendo solamente
> un bullet que describe de donde se obtuvo la evidencia (incluyendo
> ruta y/o link si aplica) y que dice en concreto (p. ej. \* evidencia
> proveniente de x.com que señala “esto, aquello y lo otro”. p. ej. 2.
> \* fichero plan.md, sección “TA TA TA”, señala “esto aquello y lo
> otro”. se ubica en c/users/yo/plan.md”. p. ej. 3. \* fichero x.py,
> líneas 34 a 36, hacen “esto, esto y esto”. Se ubica en
> c/users/yo/x.py).
>
> 4.) Análisis que explica por qué la evidencia y el correcto contraste
> de la misma apuntan inequívocamente al veredicto.
>
> • Si fue una premisa que necesitó de ajustes -rama “veredicto es
> contradicha”-, que en “Resumen por Ronda” se registre:
>
> 1.) El texto exacto de la premisa una vez fue reformulada en función
> de la retroalimentación de las fuentes -de acuerdo con el inciso b del
> paso 6-
>
> 2.) El “nuevo” veredicto: confirmada o contradicha.
>
> 3.) La ubicación de la evidencia (bajo las mismas indicaciones
> detalladas en la explicación de la rama –“veredicto es confirmada"-)
>
> 4.) El análisis detrás del veredicto (bajo las mismas indicaciones
> detalladas en la explicación de la rama –“veredicto es confirmada"-)
>
> Este registro de 1.) a 4.) existirá para cada ronda de ajuste que
> presente la premisa inicialmente contradicha, indistintamente de si es
> confirmada o permanece contradicha hasta descartada.
>
> Consideraciones Generales:
>
> De la misma forma como sucede con la propuesta de información a
> documentar en las demás columnas del registro de la bitácora (su
> desenlace), la presente propuesta para el registro documental a
> incluir en la columna “Resumen por Ronda” solo describe cual
> información se quiere documentar, en donde, de que manera, y en qué
> momentos del “ciclo de vida” de las premisas. En ningún momento
> detalla cuales son las instrucciones que deben existir en el inciso b
> del paso 6 -que es donde están las instrucciones para la confirmación
> o contradicción de las premisas y por tanto también deberían estar las
> instrucciones para que se documente en la bitácora de las premisas de
> acuerdo con esta propuesta- para que la documentación en la bitácora
> de las premisas ocurra conforme a las columnas y contenidos detallados
> en la misma. Es totalmente dependiente de dichas instrucciones en
> dicho inciso y paso del procedimiento detallado en plan-redactor.
>
> Flujo documental en la bitácora de la rúbrica
>
> Antes de detallar la propuesta de flujo documental para la información
> asociada a la graduación de la rúbrica, cabe mencionar que esta
> propuesta depende directamente de lo propuesto y/o definido a raíz de
> las respuestas asociadas a 4.), con relación a la creación de la
> bitácora y el delta para el registro de información asociada a la
> graduación de la rúbrica; incluyendo las modificaciones al plan en
> función de los ajustes que se le hacen para ver satisfecho y/o
> confirmado determinado criterio. Asumiendo que sí se crearán la
> bitácora y el delta de la rúbrica, a continuación, se detalla la
> propuesta de flujo documental asociado al registro de documentación en
> la bitácora de la rúbrica. Cabe mencionar que esta propuesta que se
> detallará a continuación también deberá ser validada contra la
> información fiable y actualizada proveniente de las máximas fuentes de
> autoridad en la materia (web + ctx 7 para confirmar) como la opción
> correcta, óptima y pertinente en nuestro caso particular para el
> registro de dicha información asociada a la graduación de la rúbrica.
> De no serlo, es necesario ajustarla con base en esa misma información
> considerando lo correcto, óptimo y pertinente en nuestro caso
> particular.
>
> Consideraciones sobre la “Bitácora de la rúbrica”
>
> A diferencia de como sucedía en el caso de la bitácora de las premisas
> (es decir, la que registra información asociada al proceso de
> confirmación o contradicción de premisas y cambios en el plan), En
> esta bitácora la principal diferencia es que las afirmaciones
> validables nunca cambian ni se ajustan sobre la marcha, puesto que
> aquí dichas afirmaciones son criterios ya definidos con los cuales el
> plan debe cumplir (es decir, que suceda que al inspeccionar el plan se
> puedan afirmar cada una de esas afirmaciones validables que
> constituyen los criterios). De esta forma, mientras que en el caso de
> las premisas las premisas per se ajustaban hasta ser confirmadas y
> solo entonces ocurrían cambios en el plan, aquí las premisas, en caso
> de ser encontradas “contradichas” se mantienen intactas, y lo único
> que debería ajustarse son las secciones del plan que hacen que el
> criterio no sea “confirmado”.
>
> Aclarado esto, se propone adoptar el enfoque “una fila, un registro”,
> de manera que la bitácora de la rúbrica registre en cada “fila” el
> “desenlace” asociado a la confirmación de cada criterio, es decir, el
> “snapshot” de la información resultante para el veredicto final de ese
> criterio. El veredicto final puede ser confirmado o contradicho y se
> obtiene al final de las rondas de inspección y ajuste sobre el plan
> que hayan sido requeridas hasta que determinado criterio sea
> “confirmado”; el mínimo de rondas de inspección y ajuste es 1 para los
> casos en los que el plan no necesite ningún ajuste para tener
> confirmado determinado criterio, y el máximo es de estas rondas es
> 3-\*\*\*\*. Adicionalmente, tal y como se especificó en el caso de la
> rúbrica, se propone incluir 3 niveles de ubicación para cada una de
> las evidencias involucradas en el análisis y contraste de las mismas
> que conduce al veredicto emitido.
>
> Sobre la ubicación de la evidencia y sus fuentes de procedencia
>
> Con relación a las fuentes de procedencia de las evidencias, aquellas
> pueden provenir de 3 tipos distintos de “fuentes” previamente
> delimitados en la propuesta del flujo documental para la bitácora de
> las premisas; el plan, fuentes “de autoridad” (como artículos,
> documentación oficial, casuística documental, etc. consultados a
> través de la web context 7; se trata de información que pueda
> encontrarse detrás de un link, o lo que corresponda en el caso de ctx
> 7) y fuentes “externas” (fichero.md, fichero.py u otras sin
> especificar, todas localizables mediante ruta a nivel de SO).
>
> Con relación a la ubicación de la evidencia, de la misma forma como se
> indicó en el caso de la bitácora de las premisas, las evidencias que
> se contrastan en el análisis que soporta la emisión de determinado
> veredicto para cada criterio evaluado son ubicadas a lo largo de 3
> niveles que van de lo “más general” a lo “más específico”, incluyendo
> la “ruta que lleva a la información”; link o ruta a nivel de SO.
> Concretamente, dichos niveles son:
>
> • Nivel 1 -\> “El grueso”: Es la pieza de información completa donde
> existe la evidencia. Es el “grueso” de la información, como un
> artículo completo proveniente de web y/o ctx 7, o si es fuente
> “externa”, sección entera del artefacto, código fuente, u otro.
>
> • Nivel 2 -\> “Parte o partes especifica(s) dentro del grueso”: Es el
> lugar -o los lugares- específicos dentro de esa pieza completa de
> información -el grueso- en donde está la evidencia exacta per se. (p.
> ej. si hablamos de evidencia dentro de un artículo entero, fichero.md
> entero o fichero.py entero, aquellos serían el “grueso”, y dentro de
> ellos, existen las secciones que contienen la evidencia exacta; en el
> caso del artículo, en algún párrafo o párrafos suyos existirán las
> oraciones que contienen evidencia utilizada en el análisis detrás del
> cual se emitió un veredicto; y lo mismo sucede con los ficheros; en
> alguna sección específica del fichero.md y/o del fichero.py existe la
> evidencia per se utilizada en el análisis detrás del veredicto. A esos
> lugares específicos donde existe la evidencia es que se refiere el
> nivel 2.)
>
> • Nivel 3 -\> “La ruta que lleva a la información”: Son los links (en
> el caso de las evidencias provenientes de fuentes de autoridad) y/o
> rutas a nivel de SO (en el caso de las fuentes externas como
> fichero.md, fichero.py, otras no especificadas y el plan) detrás de
> los que vive “el grueso” que contiene la evidencia.
>
> Filosofía de la “Bitácora de la Rúbrica”
>
> Esta bitácora se “divide en 2”: por un lado, las columnas 1 a 10
> (detalladas con mayor profundidad más adelante) detallan información
> relacionada con el “desenlace” frente a la evaluación del plan ante
> determinado criterio. Es decir, las columnas 1 a 10 contienen
> información que es única y exclusivamente relacionada con el último
> veredicto que el plan obtuvo frente a cada criterio (a excepción de la
> columna 10, que, solo en caso de que el plan no satisfaga determinado
> criterio y por consiguiente sufra de ajustes, contendrá el registro de
> un diff y por tanto si contendrá información que no “pertenece” al
> último veredicto exclusivamente -partes anteriores del plan cuando
> obtuvo contradicho determinado criterio- ). Para total claridad, las
> columnas del 1 a 9 y 10 (caso “especial”) registraran “el último” de
> lo hecho; p. ej. “El último veredicto”, “La última evidencia”, “El
> último análisis”, “La última estrategia de ajuste”, “El último
> handoff”, “El último Diff”.
>
> Por su parte, la columna 11 “Resumen por Ronda”, funge como historial
> ligero que sirve para entender la evolución de las evidencias y el
> análisis detrás de cada veredicto obtenido por el plan ante
> determinado criterio, así como para tener referenciadas las secciones
> específicas del mismo que contribuyeron a determinado veredicto.
>
> Este enfoque de registrar el “desenlace” y el “historial por ronda”,
> aunado a al paradigma de “1 fila = un registro”, constituyen la
> filosofía de la “bitácora de la rúbrica”
>
> Columnas de cada registro en la bitácora de la rubrica
>
> Mencionadas las consideración y aclaraciones sobre la evidencia, su
> procedencia, y niveles de ubicación, se propone que existan las
> siguientes nueve columnas en cada registro que se haga en la bitácora
> de la rúbrica:
>
> Columna 1: “C#” -\> el número del criterio. P. ej. “C2”
>
> Columna 2: “criterio per se” -\> el texto exacto de la afirmación
> validable que constituye el criterio. P. ej. “El plan no introduce
> antipatrones de ningún tipo en conformidad con las reglas de
> agents.md”
>
> Columna 3: “veredicto” -\> el texto exacto del veredicto final;
> “confirmado” o “contradicho”
>
> Columna 4: “El grueso de la evidencia” -\> En esta columna, debe
> incluirse la pieza de información completa donde existe la evidencia.
> P. ej. un artículo completo proveniente de web y/o ctx 7, o si es
> fuente “externa”, sección entera del artefacto, código fuente, u otro)
>
> Columna 5: La “parte en específico del grueso” -\> En esta columna, se
> indica la sección de información proveniente del grueso que contiene
> la evidencia per sé. P. ej. Las oraciones del artículo y/o partes
> dentro del artículo, las líneas de código y/o secciones dentro de
> fichero.py (o los ficheros.py), o la sección o secciones dentro de
> artefacto.md (o los artefactos.md).
>
> Columna 6: La “ruta que conduce a la información” -\> El/Los link(s) o
> ruta(s) a nivel de SO que permiten verificar la ubicación de la
> evidencia.
>
> Columna 7: El análisis -\> Aquí se registra el análisis exacto que
> detalla el contraste entre cada una de las evidencias involucradas y
> explica como dicho contraste conduce inequívocamente al veredicto
> emitido frente a determinado criterio evaluado.
>
> Columna 8: Estrategia de ajuste (se registra solo si aplica) -\> Aquí
> se detalla cuáles son las modificaciones que, con base en el análisis
> de las evidencias, el agente considere que deben hacerse al plan para
> que pase a cumplir con determinado criterio cuando tras ronda de
> inspección y ajuste exista no satisfecho o “contradicho”. Si el plan
> no requirió ajustes y satisfizo determinado criterio en su primera
> ronda de inspección y ajuste, esta columna permanece vacía o con
> placeholder “N/A” para dicho determinado criterio.
>
> Columna 9: Handoff posterior a la implementación de la estrategia de
> confirmación (se registra solo si aplica) -\>Es el informe que compara
> lo planificado para ajustarle al plan versus lo que de hecho se ajustó
> en el plan en función del cumplimiento del criterio, y en dónde. Si el
> plan no requirió ajustes y satisfizo determinado criterio en su
> primera ronda de inspección y ajuste, esta columna permanece vacía o
> con placeholder “N/A” para dicho determinado criterio.
>
> Columna 10: Diff del plan (solo si aplica) -\> Es donde se puede
> observar qué decía exactamente el plan cuando al ser contrastado
> contra determinado criterio no lo satisfizo vs que quedó diciendo el
> plan una vez fue ajustado y ante esos ajustes logró finalmente
> satisfacer el criterio inicialmente contradicho. Si el plan no
> requirió ajustes y satisfizo determinado criterio en su primera ronda
> de inspección y ajuste, esta columna permanece vacía o con placeholder
> “N/A” para dicho determinado criterio.
>
> Nótese que contrario a como sucede en el caso de la bitácora de las
> premisas, aquí solo cuando un plan aprueba un criterio a la primera
> las columnas 8, 9 y 10 quedan vacías y/o con placeholder N.A. (En el
> caso de las premisas, como solo ocurren modificaciones al plan cuando
> la premisa ha sido confirmada, entonces las “columnas homólogas” a esa
> bitácora quedan vacías en 2 escenarios; cuando la premisa es
> confirmada a la primera, o cuando no logra ser confirmada y es
> descartada).
>
> Propuesta de columna “Resumen por Ronda”
>
> Se propone, adicionalmente a las 10 columnas ya detalladas, una
> adicional que servirá para documentar la evolución del plan hasta que
> logra los ajustes que le permiten tener satisfecho determinado
> criterio de la rúbrica. Dicha columna registrará para cada ronda de
> inspección y ajuste que existiese -1 o 3 o lo que se especifique en el
> paso 6, sección c- las siguientes piezas de información: 1.) Secciones
> del plan que se inspeccionaron y que contribuyen al veredicto obtenido
> al evaluar el criterio, 2.) veredicto del plan frente al criterio, 3.)
> evidencias, 4.) análisis que explica por qué se obtuvo dicho criterio,
> en función del contraste de las evidencias y lo que aquel señala.
>
> Aclaraciones sobre las 4 piezas de información que se proponen
> registrar en esta columna 11 “Registro por ronda”
>
> Las piezas de información 2 y 4 de la columna 11 -el veredicto y el
> análisis- se registran en ella de la misma forma y con el mismo nivel
> de detalle a como esa información se registra en las columnas 3 y 7
> para el desenlace. La pieza de información 1 de la columna 11 hace
> referencia a bullets que sean específicos y exactos en referenciar
> cada parte del plan que se inspeccionó al emitir determinado
> veredicto. La pieza de información 3 de la columna 11 hace referencia
> al registro, para cada evidencia, de la “ruta que conduce a la
> información” junto con la parte específica del grueso en donde está la
> evidencia. Es decir, mientras que en “el desenlace” existen 3 columnas
> dedicadas a proporcionar la ubicación de la evidencia de forma “multi
> nivel” -niveles 3, 2 y 1-, en el caso de la columna 11 solo se
> condensarán los niveles 2 y 1.
>
> Consideraciones adicionales sobre la columna 11 “Registro por ronda”
>
> Si sucede que ante determinado criterio el plan no requiere de ajustes
> para tenerlo “confirmado” (es decir, la afirmación validable que
> constituye el criterio es confirmada y por tanto el criterio es
> satisfecho) bajo la rama “plan supera criterio a la primera”, el
> registro de esta columna se puede omitir ya que las otras 10 columnas
> tendrán toda la información relevante si se necesitase inspeccionar lo
> acontecido al graduar ese criterio.
>
> Si sucede que ante determinado criterio el plan si requirió de ajustes
> hasta cumplir con el (o nó, de acuerdo con 3.2.1)), entonces por cada
> ronda en la que el plan reciba ajustes, se tendrá que registrar en
> esta columna cada una de las 4 piezas de información ya detalladas
> (exceptuando el desenlace; puesto que las columnas 1 – 10 ya lo
> registrarán. p. ej. Si determinado criterio no satisfecho hizo que el
> plan fuera ajustado 3 veces hasta obtener su veredicto definitivo,
> entonces las columnas 1 – 10 registrarán toda la información asociada
> a ese veredicto definitivo obtenido tras el tercer ajuste, mientras
> que la columna 11 registrará el historial previo al desenlace, es
> decir, sus 4 piezas de información adjudicadas para los ajustes 1 y 2
> que presentó el plan frente a determinado criterio en específico).
>
> \*\*\*\*En lo propuesto y/o respondido a los incisos numerados 3.2) y
> 3.2.1) existe información que esclarece la forma en que se quiere que
> se itere sobre los criterios de la rúbrica al graduarla y sobre qué
> hacer en caso que un criterio no pueda ser confirmado una vez agotado
> el máximo número de rondas de ajuste por criterio.
>
> Teniendo en cuenta la propuesta completa de flujo documental detallada
> en este inciso numerado 14.) (reforma completa a la bitácora de las
> premisas e implementación de la bitácora de “La rúbrica”), debemos
> confirmar con información fiable y actualizada recogida ante las
> máximas fuentes de autoridad en la materia (ctx7 + web para confirmar)
> qué es lo que dicha información sugiere frente a si la propuesta del
> flujo documental, la propuesta de reforma completa a la bitácora de
> las premisas, y la propuesta de creación y/o implementación de la
> bitácora de la rúbrica sin son verdaderamente propuestas correctas,
> óptimas y pertinentes en nuestro caso particular y por qué, o si por
> el contrario resultan no serlo, que nos digan por qué y cuales ajustes
> serían necesarios para que, en nuestro caso particular, dicho flujo
> documental y propuesta de intervención y creación de bitácoras si sean
> propuestas correctas, óptimas y pertinentes.
>
> 15.) Una vez consultadas las fuentes y obtenida claridad sobre la
> propuesta del flujo documental, la propuesta de la reforma de la
> bitácora de las premisas y la propuesta de implementación de la
> bitácora de la rúbrica, es necesario volver a confirmar con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a cuál es la redacción exacta y lugar
> más adecuado en donde ubicar las instrucciones que permitan al
> procedimiento numerado detallado dentro de plan-redactor.md ir
> documentando en cada bitácora a medida que se confirman/contradicen
> premisas y/o se evalúa el cumplimiento de criterios en la rúbrica
> (Infiero que en todo caso hablamos de instrucciones textuales que se
> redactan en plan-redactor.md en sus secciones b y c, pero no trabajaré
> con suposicines sinó con lo que recomiende en nuestro caso particular
> esta información que estamos consultando). que esta información
> consultada nos diga la manera correcta, óptima y pertinente que
> podemos y/o deberíamos emplear en nuestro caso particular para dejar
> indicadas esas instrucciones de documentación en las bitácoras y nos
> explique por qué esa manera que nos sugiere es la correcta, óptima y
> pertinente en nuestro caso particular.
>
> <span class="mark">\*\*Hay que definir con ayuda de las
> recomendaciones de las máximas fuentes de autoridad si, en caso de
> ocurrir la rama “fuentes contradicen”, cual es el momento o la forma
> correcta, pertinente y óptima, en nuestro caso particular, de realizar
> los cambios al plan: si estos deben hacerse tan pronto ocurre el
> momento 5.) (es decir, contrario al flujo que propuse arriba, en 5) no
> se detallarían las partes a modificar del plan para solo ser
> ejecutadas las modificaciones en caso de que se confirme la premisa y
> ocurra el registro documental 6), sino que se modificarían de
> inmediato, lo que implicaría que para cuando haya un veredicto y se
> registre en 2, independientemente de su resultado, el plan ya se abría
> ajustado para reflejar la premisa reformulada y desaparecería el
> paso/momento de registro documental 6.). Debemos Confirmar con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto; las evidencias para
> confirmar o contradecir una premisa o criterio de la rúbrica, ¿se
> registran? ¿Cómo y en donde? ¿Tiene sentido en nuestro caso particular
> registrarlas? ¿mi propuesta de la bitácora, incluyendo los pasos de
> registro de información que propongo para la sección “Acciones
> Aplicadas” tiene sentido? ¿Es óptima? ¿Es sobre ingeniería? ¿Qué
> comentarios y/o sugerencias idóneas en nuestro caso particular tienen
> las fuentes? Si en el punto 4.) de este documento (que habla sobre la
> documentación en un delta inexistente de cosas que presumiblemente
> deberían ir en una bitácora inexistente) las fuentes dictaminan que
> vale la pena que tengamos bitácora para el registro de información
> relacionada con la graduación de la rúbrica, ¿acaso esa bitácora
> debería detallar la información tal y como la que estoy proponiendo
> para el registro de información asociada con la confirmación /
> contradicción de premisas? ¿qué es lo que dice esa información fiable,
> pertinente a nuestro caso particular y actualizada recolectada desde
> las máximas fuentes de autoridad en la materia que es lo correcto,
> óptimo y pertinente que podemos hacer en nuestro caso particular
> frente a todo esto y frente a cada una de mis dudas?</span>
>
> 14.1) \[DUDA COMPLEMENTARIA A 14 SOBRE CUALES DEBERÍAN SER LAS
> INSTRUCCIONES EXÁCTAS QUE SE ADICIONEN A LOS INCISOS B Y C DEL PASO 6
> DEL PROCEDIMIENTO PARA QUE SE PUEDA DOCUMENTAR LA INFORMACIÓN DE
> ACUERDO CON LAS BITÁCORAS DE PREMISAS Y RÚBRICA PROPUESTAS EN 14\] En
> 14.) se propone un flujo documental (es decir, que documentar, de que
> forma y en donde) que considera una propuesta de remodelación de la
> bitácora de las premisas, y una propuesta de implementación de la
> bitácora de la rúbrica. Sin embargo, en la sección b (confirmación
> /contradicción de premisas contra fuentes) del paso 6 del
> procedimiento detallado en plan-redactor.md, las instrucciones que
> actualmente existen sobre el registro en la bitácora no se alinean al
> flujo de documentación propuesto en 14.). Ante ello surge la duda, en
> nuestro caso particular, ¿Cuáles deberían ser las instrucciones
> exactas que permitan que a medida que las premisas son confirmadas o
> contradichas ante las fuentes se vaya nutriendo con información la
> bitácora de acuerdo con el flujo documental propuesto en 14? ¿ya
> existen? Adicionalmente, si después de consultada la propuesta de
> bitácora de la rúbrica ante las máximas fuentes de autoridad en 14.)
> resultó que, si vale la pena crearla en nuestro caso particular, ¿Si
> existen ya las instrucciones adecuadas en el inciso c del paso 6 del
> procedimiento detallado en plan-redactor.md que permitan que esa
> bitácora de la rúbrica se vaya nutriendo de acuerdo con su flujo
> documental exacto propuesto en 14 a medida que el plan se contrastando
> con cada criterio? Es necesario responder estas 3 dudas, verificando
> primero si las instrucciones ya existen -tanto para el registro en la
> bitácora de las premisas de acuerdo al flujo de 14, como para el
> registro en la bitácora de la rubrica bajo lo propuesto en ese mismo
> numeral- y luego confirmar con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar) qué es lo que dicha información sugiere frente a
> si esas instrucciones para que se nutran esas bitácoras, así como su
> ubicación, si son en verdad correctas, óptimas y pertinentes en
> nuestro caso particular, y si no es así, que ajustes valdría la pena
> que implementáramos y por qué.
>
> 16.) \[DUDA SOBRE SI DEBERÍA EXISTIR UN MECANISMO ADICIONAL QUE
> ASEGURE QUE EL PLAN ESTÁ BIEN ACOTADO\]¿Debería existir un mecanismo
> adicional de verificación sobre el plan que garantice que no se sale
> del alcance de la deuda detrás del tag? actualmente el único mecanismo
> son las instrucciones que se proporcionan en la sección análisis del
> verificador dentro de verificación.md, que es elaborado por
> deuda-verificador. Confirmar con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar) qué es lo que dicha información sugiere frente a
> todo esto y qué es lo que dice que es lo correcto, óptimo y pertinente
> que podemos hacer en nuestro caso particular.
>
> 17.) \[DUDA COMPLEMENTARIA DE 15.) SOBRE SI EL
> MECANISMO/PROCEDIMIENTO/INSTRUCCIÓN TEXTUAL ACTUAL QUE SE ENCARGA DE
> DEFINIR EL ALCANCE DEL PLAN ES EL CORRECTO, PERTINENTE Y ÓPTIMO EN EL
> CASO PARTICULAR DEL FLUJO AGÉNTICO\] El mecanismo actual del cual
> depende que a partir de las instrucciones de plan-redactor el agente
> pueda construir el plan que resuelve el problema correcto en términos
> de alcance, es decir, la deuda específica detrás de un tag en todo el
> repo, es el de instruir al agente que “absorba” el fichero
> verificacion.md -incluyendo lectura de la sección “análisis del
> verificador”-. Aclarado eso, se plantea la duda: ¿ese mecanismo (“paso
> 1 del procedimiento y su redacción de absorber verificación.md”) si
> existe de la forma correcta en nuestro caso particular y garantiza que
> al agente y/o subagente que sigue las instrucciones de plan redactor
> le quede claro cuál es el alcance correcto del plan todas las veces,
> de forma que produzca resultados aceptablemente deterministas en una
> escala profesional? La duda surge del siguiente razonamiento: las
> premisas sobre las que se elabora el plan no sólo deben ser correctas
> (fuentes las avalan o de no existir fuentes aplicables, el agente hace
> lo correcto para tener evidencia sólida que sustente la decisión) sino
> que deben contribuir a saldar la deuda técnica correcta todas las
> veces. Como las premisas son afirmaciones validables que se desprenden
> del plan, por eso la duda.. Nuestro actual mecanismo para que el plan
> quede bien acotado, ¿si es el correcto en nuestro caso particular?
> ¿basta con que las instrucciones que lee el agente dentro de plan
> redactor digan \*\*absorbe\*\* para que este (el agente) entienda bien
> y todas las veces que debe construir un plan orientado a resolver esa
> deuda técnica puntual? ¿vale la pena redundar y decirle en la sección
> b del paso 6 que las premisas deben contribuir a saldar deuda técnica?
> Confirmar con información fiable y actualizada recogida ante las
> máximas fuentes de autoridad en la materia (ctx7 + web para confirmar)
> qué es lo que dicha información sugiere frente a todo esto y qué es lo
> que dice que es lo correcto, óptimo y pertinente que podemos hacer en
> nuestro caso particular.
>
> 16.1) \[DUDA COMPLEMENTARIA A 16.) – CLARIDAD DE INSTRUCCIONES PARA EL
> AGENTE Y DUDAS SOBRE SI PERMITEN CONSISTENCIA EN SUS RESULTADOS A LA
> HORA DE CONSTRUIR EL PLAN BASÁNDOSE EN LO QUE DICE LA SECCIÓN ANÁLIZIS
> DEL VERIFICADOR\] la sección análisis del verificador, ¿si es lo
> suficientemente explícita en definir con claridad el alcance correcto
> para el plan todas las veces? ¿cuál es la forma correcta en nuestro
> caso particular de garantizar que sí haya esa claridad todas las
> veces? Esta pregunta se hace suponiendo que las fuentes previamente
> hayan verificado que este mecanismo (utilizar la sección análisis del
> verificador dentro de verificación.md como insumo primario para que el
> agente que sigue las instrucciones de plan-redactor cree el plan) es
> el pertinente en nuestro caso particular para garantizar que el agente
> construya el plan que resuelve el problema correcto todas las veces.
> Es necesario, por lo tanto, que esta pregunta se resuelva considerando
> a detalle la respuesta al inciso numerado 16.). Dicho eso, si la
> respuesta al inciso numerado 16 es que la información de las máximas
> fuentes de autoridad proporciona evidencia sólida y veraz que confirme
> que lo más pertinente, óptimo y adecuado en nuestro caso particular es
> seguir trabajando con el mecanismo de usar análisis del verificador
> como insumo primario para la construcción del plan, entonces confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere sobre cuál es la forma correcta en nuestro
> caso particular de hacer que el análisis del verificador sea
> absolutamente claro para cualquier agente que lea verificacion.md, y
> que a ese agente no le quepa duda de que debe exactamente resolver el
> plan, y que no debe tocar, y que de esta forma produzca resultados
> aceptablemente deterministas dentro de una escala profesional; qué es
> lo que dice la información que es lo correcto, óptimo y pertinente que
> podemos hacer en nuestro caso particular.
>
> 16.2) \[DUDA COMPLEMENTARIA A 16.) SOBRE SI EL ACTUAL PROCEDIMIENTO
> Y/O INSTRUCIONES DE PLAN REACTOR SI SON LOS CORRECTOS EN NUESTRO CASO
> PARTICULAR PARA QUE OCURRA LA DEBIDA COREOGRAFÍA DE PRIMERO CONSTRUIR
> EL BORRADOR “0” Y DESPUÉS OBTENER LAS PREMISAS PARA VALIDACIÓN CONTRA
> LAS FUENTES, Y DUDA SOBRE SI LA INSTRUCCIÓN “CONFIRME CON FUENTES
> -PASO 6, INCISO B-” ES SUFICIENTE O NÓ\] Si bien es cierto que ya
> existe un procedimiento claro con pasos numerados dentro del plan
> redactor en el que se le indica que primero tiene que absorber,
> contrastar, ampliar, construir el análisis y redactar antes de validar
> contra fuentes de autoridad, surgen las dudas siguientes: En nuestro
> caso particular, ese procedimiento con pasos numerados en donde el
> sexto es contrastar con fuentes de autoridad, ¿si es el adecuado? ¿si
> permite para validar el plan contra fuentes de autoridad de forma
> correcta?
>
> Dentro de ese procedimiento numerado, en el paso 6, el mecanismo de
> “instruir al agente que obtenga las afirmaciones validables (premisas)
> del primer borrador del plan -paso 6, inciso b” para que después “vaya
> y las confirme contra fuentes de autoridad”, ¿Si es el adecuado para
> contrastar el plan contra fuentes de autoridad? ¿Es un mecanismo que
> permite el suficiente determinismo en los resultados (planes siempre
> se verifican contra fuentes de autoridad de determinada forma -que es
> la correcta- todas las veces) como para ser profesionalmente útil?
> ¿Habría que agregarle algo al procedimiento de los 7 pasos (me refiero
> al procedimiento con los pasos absorber, contrastar, ampliar, etc) o
> al mecanismo (cree el plan, luego saque sus premisas, luego vaya y
> contraste contra fuentes para confirmar o contradecir las premisas)
> para que contribuyan de mejor forma a confirmar de forma correcta el
> primer borrador del plan contra fuentes de autoridad, o ya tienen todo
> lo necesario (procedimiento 7 pasos y mecanismo “construir plan -\>
> extraer premisas -\> confirmar/contradecir contra fuentes”) para
> funcionar de forma que el agente que lea esas instrucciones realice un
> trabajo aceptablemente determinista bajo una escala profesional todas
> las veces, trabajo que además sirva todas las veces para validar de
> forma correcta el primer borrador del plan ante fuentes de autoridad?
> confirmar con información fiable y actualizada recogida ante las
> máximas fuentes de autoridad en la materia (ctx7 + web para confirmar)
> qué es lo que dicha información sugiere frente a todo esto y qué es lo
> que dice que es lo correcto, óptimo y pertinente que podemos y/o
> deberíamos (o nó) hacer en nuestro caso particular y por qué.
>
> 16.2.1) \[DUDA COMPLEMENTARIA A 16.2) – INCLUIR CRITERIO/PROCEDIMIENTO
> GUIA QUE INSTRUYA AL AGENTE SOBRE COMO EXÁCTAMENTE DEBE EXTRAER Y/O
> OBTENER LAS AFIRMACIONES VALIDABLES (PREMISAS) QUE SE
> CONFIRMARÁN/CONTRADIRÁN EN EL PASO 6, INCISO B.\] Si la respuesta al
> inciso numerado 16.2 resulta ser que la información consultada ante
> las máximas fuentes de autoridad corroboran que tanto el procedimiento
> de 7 pasos como el mecanismo de verificación del primer borrador del
> plan contra fuentes de autoridad (construir plan -\> obtener sus
> premisas -\> decirle al agente “ve y usa determinadas fuentes para
> confirmar o contradecir las premisas”) si son los correctos,
> pertinentes y óptimos en nuestro caso particular, entonces surge la
> siguiente duda: Si bien es cierto que actualmente existe (o se
> implementará) un mecanismo para que el agente extraiga del borrador
> del plan afirmaciones validables (decisiones estructurales,
> trade-offs, orden de fases, alcance y residuos, -tal y como se detalla
> en la sección a del paso 6- ), que luego irá a contrastar con las
> fuentes para “confirmarlas o contradecirlas”, surge la duda de, ¿vale
> la pena agregar un procedimiento y/o mecanismo y/o criterio guía para
> que el agente sepa cómo exactamente es que debe identificar cuáles son
> esas afirmaciones validables que tiene que extraer del plan para
> convertir en premisas que luego irá a contrastar contra las fuentes?
> ¿O se puede delegar esto enteramente a su criterio propio? Confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos y/o deberíamos (o nó)
> hacer en nuestro caso particular y por qué.
>
> 18.) \[DUDA SOBRE SI LA REDACCIÓN TEXTUAL PRESENTE EN PLAN-REDACTOR
> PERMITE UTILIZAR ADECUADAMENTE LOS INSUMOS QUE SE PROPORCIONAN EN LA
> SECCIÓN RE-AUDITORÍA DEL FICHERO VERIFICACION.MD\] ¿Las instrucciones
> de Plan-redactor permiten al agente que las lea utilizar adecuadamente
> los insumos de la sección reauditoria que se detalla en
> deuda-verificador? ¿la redacción actual \*\*absorber\*\* en plan
> redactor.md sí es la que le permite al agente que se guía sobre las
> instrucciones del plan-redactor utilizar verificación.md de la mejor
> forma? ¿qué es lo que dice las máximas fuentes de autoridad? Confirmar
> con información fiable y actualizada recogida ante las máximas fuentes
> de autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos hacer en nuestro caso
> particular.
>
> 19.) \[OBSERVACIÓN CRÍTICA – LA DEUDA SE DESMIENTE/CONFIRMA CONFIANDO
> ENTERAMENTE EN QUE EL INFORME DE AUDITORÍA (.HTML) YA ENCONTRÓ
> EXÁCTAMENTE A DONDE ESTÁ LA DEUDA, PERO NO SE LE DICE EXPLICITAMENTE
> AL AGENTE QUE NO SE BASE SOLO EN LO INDICADO EN LA AUDITORÍA SINO QUE
> ADEMÁS CONDUZCA SU PROPIA INVETIGACIÓN ANTES DE EMITIR EL VEREDICTO
> SOBRE LA EXISTENCIA DE LA DEUDA\] deuda-verificador marca la deuda
> como confirmada parcial o desmentida basándose en su lectura de cómo y
> en dónde se presenta la deuda de acuerdo al tag y no de acuerdo a lo
> dicho en el tag junto con una búsqueda y análisis exhaustivo de todo
> el código del repositorio que corrobore si de verdad la deuda solo
> existe donde lo dice el informe o si sucede que está presente en
> rincones del código no detallados ni implícita ni explícitamente en el
> informe.

Esto es muy peligroso porque favorece escenarios en donde la deuda
técnica se marca como “desmentida” aún si en realidad existe solo que
por fuera de los lugares que inicialmente detectó la auditoría (debido a
limitantes del agente que elaboró el informe .html o a modificaciones en
el código a posteriori de la emisión del informe .html). Por ejemy 2 si
en el futuro se añade código que vuelve a introducir deuda técnica
relacionada con el tag d1 (scattered auth logic), si esa deuda no se
introduce exactamente en los lugares donde el informe la encontró por
primera vez, de acuerdo a las instrucciones actuales de
deuda-verificador, el agente que siga sus instrucciones (y más
específicamente su procedimiento) irá a buscarla únicamente en los
lugares donde el informe la referencia (de acuerdo a los pasos 1 y 2 del
procedimiento, donde no se le pide explícitamente que busque en todo el
código y no solo a donde el informe dice que está la deuda). Entonces se
revisará los rincones del código y/o ficheros que el .html de la
auditoría señala como lugares de existencia de la deuda, como la deuda
no se introdujo exactamente allí y como al agente no se le dijo
explícitamente que fuera a buscarla en todo el código antes de emitir un
veredicto, pues es altamente presumible que seguirá las instrucciones
proporcionadas y por tanto marcara la deuda d1 como “desmentida”, aún
cuando esta puede existir solo que en otros rincones del código no
especificados en el .html de la auditoria.

En adición a esto, otro descubrimiento bastante grave es que no existen
instrucciones específicas para el agente que le aclaren qué debe hacer
si encuentra “desmentida” la deuda; ¿Se detiene y emite informe con
veredicto “desmentida” para la deuda detallando en el análisis del
verificador que la deuda no existe en el repositorio y que por tanto no
se dan indicaciones sobre lo que el plan debe resolver? ¿qué debería
hacer plan-redactor al leer que el análisis del verificador marca la
deuda como desmentida? ¿debería plan-redactor instruir en este caso al
agente que lo lee (que lee las instrucciones de plan-redactor) para que
corrobore que la deuda en verdad esta desmentida o acaso eso no conviene
en nuestro caso particular? Volviendo a hablar del agente que se guía de
acuerdo con las instrucciones de deuda-verificador.md, si la deuda es
“desmentida”, ¿acaso debería seguir leyendo las instrucciones de
deuda-verificador de arriba abajo y de izquierda a derecha? Si hace esto
último, ¿cuáles podrían ser sus comportamientos y decisiones con
relación a la deuda que acaba de “desmentir”, al resto de las
instrucciones presentes en deuda-verificador.md, y frente al artifact
verificacion.md? con la deuda ya marcada como “desmentida “¿ejecuta el
paso 3 del procedimiento? Si lo hace y encuentra que la deuda si existe,
¿corrige su veredicto de “desmentida” a “parcial/confirmada”? ¿tendría
sentido que marque deuda como “desmentida” sin corroborar con el resto
del código primero? ¿en qué momento emitiría verificación.md? ¿lo
emitiría con un falso negativo para después que revise (procedimiento,
paso 3) tener que corregirlo o sencillamente al ver que la deuda que
dice el .html de la auditoria no existe donde dicha auditoria dice que
está la marcaría como “desmentida” y ni siquiera se tomaría el trabajo
de leer los demás pasos del procedimiento (3, 4 , etc) y/o secciones del
fichero deuda-verificador.md?

Actualmente, es evidente que la sección reglas de deuda-verificador.md
así como el paso 3 de su procedimiento le instruyen al agente de que se
espera que exista un proceso de corroboración contra el código fuente,
pero bajo mi criterio opino que se esta confiando demasiado en que el
agente será capaz de unir los puntos e inferir que antes de emitir un
juicio sobre el estatus de la deuda debe primero corroborar contra el
código. Adicionalmente, yo infiero que aún no existen indicaciones
absolutamente claras sobre qué debe hacer el agente que lee las
instrucciones de verificacion.md en cada escenario posible, que permitan
saber con precisión cual es la respuesta exacta a cada una de las dudas
que mencioné arriba. Puede que aún haya un número significativo de
preguntas cuya respuesta en este momento dependa en su totalidad de lo
que al agente (la IA) decida hacer bajo su propio criterio, pues en
realidad el procedimiento falla en esclarecer con exactitud que se debe
hacer en cada posible caso para minimizar la posibilidad que la IA haga
“lo que se le dé la gana”. No obstante, debemos confirmar con
información fiable y actualizada recogida ante las máximas fuentes de
autoridad en la materia (ctx7 + web para confirmar) qué es lo que dicha
información sugiere frente a todo esto y qué es lo que dice que es lo
correcto, óptimo y pertinente que podemos hacer en nuestro caso
particular. Hay que usar esa información para responder las preguntas
¿El mecanismo empleado es el correcto solo que le hace falta
instrucciones más claras? ¿Vale la pena, en nbuestro caso particular,
emplear otro mecanismo? Si el mecanismo actual es el correcto, ¿Qué
ajustes se le deberían o no hacer y/o cual es la forma correcta,
pertinente y óptima, en nuestro caso particular, de lograr que esas
instrucciones sean claras e infalibles, para que el resultado de que un
agente siga las instrucciones de deuda-verificador sea lo más
determinista posible y útil para con el propósito fundamental de deuda
verificador (proporcionar al plan-redactor la información que le permite
saber correctamente cual es el problema que resolver)? ¿Cuál es la forma
correcta y óptima en nuestro caso particular de hacer que el agente se
asegure de revisar primero todo el código fuente antes de marcar la
deuda como confirmada parcial o desmentida? Considerando que revisar
todo el código fuente puede ser agotador, ¿cuál es la forma correcta de
gestionar el agotamiento del agente? ¿conviene subdelegar? - esta duda
está directamente relacionada con el inciso numerado 12 -. Todo esto es
para consultar con las fuentes de la forma ya especificada (web + ctx 7
para confirmar, solo información fiable y actualizada proveniente de las
máximas fuentes de autoridad en la materia y que sea útil en nuestro
caso particular). Las últimas 2 dudas requieren que nos remitamos a lo
esclarecido en el inciso numerado 12 y entendamos como aplicarlo en el
caso de deuda-verificador y/o si ya se aplica algo relacionado con ese
inciso para ese subagente, verificar que siga allí y que siga haciendo
sentido.

> 20.) \[DUDA SOBRE SI VALE LA PENA DEFINIRLE CRITERIOS GUÍA AL AGENTE
> SOBRE LOS CUALES APOYARSE CUANDO TENGA QUE EMITIR JUICIO BAJO SU
> CRITERIO SOBRE LA CONFIRMACIÓN DE UNA PREMISA Y/O CRITERIO\] en los
> falsos BYC del punto 6 cuando no exista una fuente aplicable para
> confirmar o contradecir una premisa o criterio de la rúbrica, ¿valdría
> la pena especificar y o definir criterios vía bajo los cuales el
> agente pueda tener luces sobre en qué fijarse para tomar cada
> decisión? Identifico que el agente puede ser capaz de confirmar o
> contradecir una premisa pero tal vez puede que tenga sentido decirle
> en el caso de las premisas qué cosas no olvidé verificar antes de
> emitir un juicio en el caso de los criterios de la rúbrica identifico
> que los criterios son bastante claros y el agente usará sus propios
> criterios para dictaminar si el plan propuesto cumple o no con
> determinado criterio de la rúbrica y en caso que tenga que
> inspeccionar fuentes externas como el código fuente etcétera tal vez
> allí sí habría espacio para delimitar criterios pero todo esto es
> inferencia mía, por eso es necesario confirmar con información fiable
> y actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 21.) \[DUDA SOBRE SI VALE LA PENA O NO REMOVER REDUNDANCIA EN RAMA
> -FUENTES CONTRADICEN- DEL PASO 6, INCISO B\] En el inciso b del paso
> 6, en la rama -la premisa es contradicha- existe una aclaración sobre
> lo que debe hacer el agente si no encuentra fuentes aplicables para
> confirmar o descartar determinada premisa. Sin embargo, mas abajo en
> esa sección ya existe una rama “-no encontraste ninguna fuente de
> autoridad aplicable” en donde se aclara exactamente lo mismo,
> generándose una redundancia frente a esa aclaración de las
> instrucciones que debe seguir el agente si no encuentra fuente
> aplicable. ¿Vale la pena conservar esa redundancia o no? Confirmar con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) qué es lo que
> dicha información sugiere frente a todo esto y qué es lo que dice que
> es lo correcto, óptimo y pertinente que podemos y/o deberíamos (o nó)
> hacer en nuestro caso particular y por qué.
>
> 22.) \[DUDAS SOBRE EL PRESUMIBLE VERDADERO PROPÓSITO Y UBICACIÓN EN
> FUNCIÓN DEL MISMO DEL INCISO E DEL PASO 6\] Si bien el inciso e del
> paso 6 contiene instrucciones de que los hallazgos fuera del alcance
> del TAG deben ir a sección de residuales y nunca al plan, para el
> procedimiento de graduación de la rúbrica sucede que dentro del inciso
> que le corresponde, que es el c, no existen instrucciones explícitas,
> claras y exactas que instruyan al agente sobre qué debe hacer cuando
> encuentra hallazgos que están por fuera del alcance del plan. En ese
> orden de ideas, surgen las siguientes dudas: ¿acaso el inciso e del
> paso 6 tiene como propósito contener las indicaciones para que el
> agente sepa que, durante el proceso de graduación de la rúbrica, que
> si encuentra trabajo futuro (es decir, fuera del alcance del tag) debe
> registrarlo específicamente en la sección “residuales”? ¿acaso el
> inciso e debería dejar de existir para convertirse en una instrucción
> existente dentro del inciso c, de manera que el proceso de graduación
> de la rúbrica que allí sucede cuente con instrucciones propias que
> indiquen al agente cuando debe ir a documentar qué cosas en
> “residuales”? hay que considerar que actualmente el inciso e parece
> una especie de “filtro global” de cumplimiento frente a la
> documentación del trabajo futuro en residuales, pero eso deja al
> proceso de graduación de la rúbrica desprovisto de aquellas
> instrucciones de documentación del trabajo futuro, mientras que el
> otro proceso (confirmación/contradicción de premisas) donde podría
> surgir trabajo futuro si cuenta con instrucciones dentro de su inciso
> frente a la documentación del mismo. Si se mueve e a que exista dentro
> del inciso c, hay que tomar en consideración la respuesta a 21.2. Si e
> se convierte en instrucción dentro de c ¿valdría la pena igualmente
> que existiera un “mecanismo global” que le refuerce al agente la idea
> de que el trabajo futuro siempre va a “residuales”? si eso se hiciera
> ¿valdría la pena implementar otros “mecanismos globales” para los
> otros mecanismos de documentación? Confirmar con información fiable y
> actualizada recogida ante las máximas fuentes de autoridad en la
> materia (ctx7 + web para confirmar) qué es lo que dicha información
> sugiere frente a todo esto y qué es lo que dice que es lo correcto,
> óptimo y pertinente que podemos y/o deberíamos (o nó) hacer en nuestro
> caso particular y por qué.
>
> 21.1) \[DUDAS COMPLEMENTARIAS A 21.) SOBRE EL MECANISMO DE REGISTRO EN
> LA SECCIÓN “RESIDUALES” QUE ACTUALMENT EXISTE EN EL INCISO E DEL PASO
> 6 (PERO QUE, DE ACUERDO A 21, PUEDE QE DE HECHO DEBA PASAR A EXISTIR
> DENTRO DEL INCISO C COMO UNA INSTRUCCIÓN ESPECÍFICA QUE SE EJECUTE
> MIENTRAS SE ESTÁ GRADUANDO LA RÚBRICA) Y SOBRE SUS INSTRUCCIONES
> ASOCIADAS\] En el inciso e del paso 6 se dice al agente que si
> encuentra hallazgos fuera del alcance del tag al inspeccionar
> diferentes “fuentes externas” (no “fuentes de autoridad” sino “fuentes
> externas”; las “fuentes de autoridad” que yo menciono hacen referencia
> a las fuentes que se le instruye consultar al agente en el inciso b
> del paso 6, para confirmar o contradecir premisas, mientras que las
> “fuentes externas” son aquellas que se le instruye al agente consultar
> en el inciso c del paso 6, al graduar la rúbrica, específicamente en
> C2) para emitir juicio sobre determinados criterios, que los envíe a
> la sección de residuales del plan. Frente a ello surge la siguiente
> duda, ¿en qué escenarios un agente encuentra trabajo futuro que
> debería irse a residuales al graduar la rúbrica? ¿Si es posible que un
> plan cuyas premisas hayan sido debidamente confirmadas introduzca
> trabajo que debiera ser futuro y que se sale del alcance del TAG? ¿O
> acaso el inciso e.) se trata de un fail safe que muy seguramente nunca
> va a ocurrir porque un plan que introduzca scope creep la sección b no
> le permite avanzar hasta la sección c, y por lo tanto, “nunca”
> ocurriría que algo de hecho termine en “residuales” por acción del
> inciso e.) ?

Adicionalmente, en el inciso e.) no se le instruye al agente sobre “cuál
es su protocolo de inspección al plan” o “a donde debe mirar” y, en
función de ello, “en qué momento puede estar seguro que el plan
introduce scope creep”, de manera que no existen instrucciones claras de
acuerdo con las cuales el agente sepa que es momento de registrar algo
en residuales; se “confía” en su criterio propio. ¿Esto si debiera ser
así? En adición a lo anterior, tampoco se le especifica al agente un
criterio guía o instrucciones claramente especificadas sobre qué otras
acciones adicionales debería realizar una vez el “protocolo de
inspección al plan”-actualmente inexistente que menciono más arriba-
permita al agente “saber” que el plan introduce scope creep, para
asegurarse con evidencia que el plan de verdad introduce trabajo fuera
del alcance del TAG, como por ejemplo decirle al agente que contraste la
presunta evidencia de que el plan introduce cosas fuera del alcance
contra el código fuente y que solo después de ejecutar estas otras
“acciones adicinales de verificación” y confirmar que hay scope creep,
vaya a residuales y lo documente. Debemos confirmar con información
fiable y actualizada recogida ante las máximas fuentes de autoridad en
la materia (ctx7 + web para confirmar) qué es lo que dicha información
sugiere frente a todo esto y qué es lo que dice que es lo correcto,
óptimo y pertinente que podemos y/o deberíamos (o no) hacer en nuestro
caso particular y por qué.

> 21.1.1) \[OBSERVACIÓN COMPLEMENTARIA A 21.1 SOBRE AUSENCIA DE
> INSTRUCCIONES DE “AJUSTAR EL PLAN” SI ESTE INTRODUCE SCOPE CREEP Y
> ESTO ES DETECTADO AL GRADUAR LA RÚBRICA\] Puede que con lo que se haya
> respondido en 21 y 21.1 suceda que el proceso de graduación de la
> rúbrica (inciso c, paso 6) tenga resuelta la situación frente a las
> instrucciones de documentación de trabajo futuro. Sin embargo, si
> resulta que si vale la pena que en el inciso c existan instrucciones
> de documentación del trabajo futuro en residuales (eso se esclarece al
> responder 21.1), sucede que actualmente no existen ni se ha planteado
> la creación de instrucciones claras para el agente que le permitan
> saber cómo debería proceder y/o que debería hacer con el borrador del
> plan para el cual, durante la graduación de la rúbrica, se identificó
> que introducía scope creep. Es decir, yo infiero que no basta solo con
> documentar el trabajo futuro en residuales, sino que adicionalmente el
> plan debería ser ajustado para que deje de introducir scopre creep y
> frente a ello me pregunto ¿ En nuestro caso particular, ¿cuáles
> deberían ser las instrucciones explicitas, claras y exáctas que se le
> proporcionen al agente con las que haga los ajustes pertinentes y de
> la forma correcta y adecuada al plan para que lo ajuste a que deje de
> introducir scope creep mientras sigue siendo verdad que las premisas
> registradas en la bitácora son reflejo fiel de lo que propone el plan,
> y mientras también sigue siendo verdad que para cada criterio con
> veredicto final emitido -al final de las x rondas por criterio- sigue
> siendo reflejo de evidencias que lo soportan, y, adicionalmente, sin
> que las reglas introducidas en 10.) impidan la realización de estos
> cambios? Es decir, los cambios al plan deben hacer que este deje de
> introducir scope creep pero necesariamente deben asegurarse de que una
> vez haya sido ajustado para ello, cada premisa ya confirmada se siga
> reflejando en la totalidad del plan, a la vez que también cada
> veredicto sobre criterios de la rúbrica sigua siendo reflejo de la
> evidencia que los soporte. ¿En qué parte exacta de plan-redactor
> -infiero que en el inciso c, pero no se en cual de sus partes- se
> deberían ubicar dichas instrucciones sobre ajustes al plan para que
> este deje de introducir el scope creep detectado mientras se graduaba
> la rúbrica? Debemos confirmar con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar) qué es lo que dicha información sugiere frente a
> todo esto y qué es lo que dice que es lo correcto, óptimo y pertinente
> que podemos y/o deberíamos (o nó) hacer en nuestro caso particular y
> por qué.
>
> 21.1.1.2) \[DUDA COMPLEMENTARIA A 21.1.1 SOBRE SI VALE LA PENA INCUIR
> CRITERIO ADICIONAL EN LA RUBRICA QUE OBLIGUE AL AGENTE A VERIFICAR QUE
> EL PLAN, UNA VEZ GRADUADO CONTRA LOS CRITERIOS C1 A C4 DE LA RÚBRICA,
> Y UNA VEZ AJUSTADO SIN QUE EL PLAN DEJE DE REFLEJAR LAS PREMISAS NI
> TAMPOCO LAS EVIDENCIAS DE LOS CRITERIOS CON VEREDICTO FINAL EMITIDO,
> NO INTRODUCE SCOPE CREEP -TENTATIVO C5- \] Si bien es cierto que
> existen mecanismos cuyo trabajo es asegurar que el plan se construya
> para resolver el problema correcto (la deuda detrás del tag presente
> en todo el repo), infiero que podría ocurrir que, en ajustes hechos al
> plan durante la graduación de la rúbrica (puede que incluso en ajustes
> hechos al plan durante la confirmación / contradicción de premisas),
> se termine por introducir scope creep. Frente a ello, y considerando
> que en 21.1.1) ya se plantea la necesidad de hallar la forma correcta,
> óptima y pertinente en nuestro caso particular de instruir al agente
> sobre como debería ajustar al plan si durante la graduación de la
> rúbrica se encuentran partes de este que introducen scope-creep, surge
> la duda complementaria: en conjunto a esas instrucciones ¿Debería
> existir un criterio adicional en la rúbrica que se encargue de
> verificar que el borrador del plan que está a punto de ser entregado
> para revisión del humano (yo) efectivamente no cuenta con scope creep?
> Este criterio adicional que propongo tendría, en todas la veces, que
> ser confirmado, independientemente de si las instrucciones que se
> desprenden de 21.1.1 entraron en acción una o más veces para ajustar
> el plan por detección de que introducía scope creep antes de que sea
> “el turno” de graduar este criterio que propongo; es decir, el hecho
> que se “remueva” scope creep detectado al graduar la rúbrica no exime
> al plan de ser, en todo caso, evaluado contra este criterio adicional
> que propongo. Debemos confirmar con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar) qué es lo que dicha información sugiere frente a
> todo esto y qué es lo que dice que es lo correcto, óptimo y pertinente
> que podemos y/o deberíamos (o nó) hacer en nuestro caso particular y
> por qué.
>
> 23.) \[OBSERVACIÓN Y DUDA SOBRE REDACCIÓN EN RAMA “LA FUENTE
> CONTRADICE” DEL INCISO B DEL PASO 6\] En el inciso b, del paso 6, en
> la rama “la fuente contradice”, cuando se especifica que si las
> recomendaciones de la fuente hechas a una premisa que, por agotar su
> máximo de rondas de ajuste y seguir estando en “contradicha” será
> descartada están dentro del alcance del plan, entonces se adopten, la
> redacción actual es: “si la recomendación de la fuente cae DENTRO del
> alcance del tag, adóptala” y yo me cuestiono ¿valdría hacer que la
> redacción quede así: “si la recomendación de la fuente hecha a esa
> premisa que se descarta cae DENTRO del alcance del tag, adóptala”?
> confirmar con información fiable y actualizada recogida ante las
> máximas fuentes de autoridad en la materia (ctx7 + web para confirmar)
> qué es lo que dicha información sugiere frente a todo esto y qué es lo
> que dice que es lo correcto, óptimo y pertinente que podemos y/o
> deberíamos (o nó) hacer en nuestro caso particular y por qué.
>
> 24.) \[DUDAS SOBRE SI TIENE SENTIDO QUE PLAN-REDACTOR PROPORCIONE
> INSTRUCCIONES QUE OBLIGUEN AL AGENTE A VERIFICAR CONTRA LA TOTALIDAD
> DEL CÓDIGO FUENTE DÓNDE EXACTAMENTE ESTÁ LA TOTALIDAD DE LA DEUDA
> TÉCNICA ANTES DE PROCEDER A CONSTRUIR EL “BORRADOR 0 ” DEL PLAN -EL
> “BORRADOR 0” ES EL BORRADOR QUE SE CREA ANTES DE LLEGAR AL PASO 6,
> DONDE SUFRE MODIFICACIONES EN FUNCION DE LA CONFIRMACIÓN DE PREMISAS
> Y/O CRITERIOS-\] ¿Tiene sentido en nuestro caso particular que el
> agente lea en el plan redactor instrucciones sobre buscar la deuda en
> todo el repositorio en caso que a deuda verificador se le haya pasado
> por alto la deuda en algún lugar del código? ¿Eso ya sería una
> sobrecarga contraproducente a la memoria de trabajo y/o ventana de
> contexto del agente y/o subagente? ¿Acaso estaríamos rompiendo el
> principio de single responsability? ¿Qué escenario permite obtener
> mejores resultados?; ¿Confiar en deuda verificador o hacer que plan
> redactor tenga instrucciones para el agente que lo obliguen a
> verificar que se haya identificado cada archivo con la deuda? Mi
> pensamiento es que Plan Redactor debe o debería verificar el alcance
> de la deuda y verificar que esta ha sido encontrada en todos los
> rincones del código donde exista. Es decir, no debería confiar
> “ciegamente” en la sección “análisis del verificador” que le
> proporciona deuda verificador en el artefacto verificacion.md. Sin
> embargo, es necesario verificar con las fuentes.

Cabe mencionar que actualmente, en plan redactor existe la sección
“AMPLIAR”, pero considero que la redacción textual que tiene no es lo
suficientemente explícita en decirle al agente que debe asegurarse de
tomar en cuenta el análisis del verificador y los ficheros con la deuda
que allí se detallen y adicionalmente verificar por su cuenta contra la
totalidad del código fuente cuales son en definitiva todos los ficheros
que poseen la deuda. Debemos confirmar con información fiable y
actualizada recogida ante las máximas fuentes de autoridad en la materia
(ctx7 + web para confirmar) qué es lo que dicha información sugiere
frente a todo esto y qué es lo que dice que es lo correcto, óptimo y
pertinente que podemos y/o deberíamos (o nó) hacer en nuestro caso
particular y por qué.

> 25.) \[DUDA SOBRE GAP.MD GENERADO POR HANDOFF-AUDITOR Y SOBRE EL “BUEN
> TRABAJO” QUE PUEDAN O NÓ HACER LAS SESIONES AUTÓNOMAS EJECUTORAS A LA
> HORA DE IMPLEMENTAR SUS FASES CORRESPONDIENTES DEL PLAN + EN CASO DE
> EXISTIR GAP, QUE SE LE DEBE AJUSTAR AL PROMPT PARA ELLO QUE
> PORPORCIONA PLAN-REDACTOR\] ¿Son los gaps el registro de las
> discrepancias entre lo que la sesión autónoma dijo que hizo y lo que
> de hecho hizo? Se puede inferir que las sesiones ejecutoras de fases
> van a tender a decir que ejecutaron el plan al pie de la letra por
> complacencia. ¿Cómo evitar esto? ¿Acaso las sesiones autónomas
> verifican y/o son provisionadas con un checklist para que puedan
> verificar que sí ejecutaron de forma correcta y completamente el plan
> y entregar el handoff solo después de verificado ese checklist? Al
> prompt del gap que me entrega plan redactor, aparte de pasarle la fase
> y el tag, ¿debo pasarle los hallazgos del handoff auditor o el ya está
> listo para usar el gap.md de forma correcta? ¿Qué otras cosas debo
> pasarle a ese prompt? Debemos confirmar cada cosa; algunas dudas se
> resuelven inspeccionando los ficheros del flujo agéntico per sé, y
> algunas otras consultando con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar). Quiero que me respondas primero las dudas que se
> resuelven inspeccionando los ficheros del flujo agéntico per se, y que
> luego de ello, ya teniendo un mejor contexto de como funcionan las
> piezas del flujo involucradas en esa respuesta, consultemos con
> información fiable y actualizada recogida ante las máximas fuentes de
> autoridad en la materia (ctx7 + web para confirmar) sobre qué es lo
> que dicha información sugiere frente a si las sesiones autónomas que
> reciben los prompts entregados por plan-redactor en el artefacto que
> genera (plan.md) tienden a responder con complacencia o no y cual es
> la forma correcta, óptima y pertinente que podemos y/o deberíamos (o
> nó) hacer en nuestro caso particular para evitar esto y por qué dicha
> forma es la correcta, óptima y pertinente en nuestro caso particular.
>
> Después de esto, quiero que acudamos a las mismas fuentes para que
> auditemos que tan correcta, optima y pertinente es, en nuestro caso
> particular, la manera como se resuelve en el flujo agentico cuando
> handoff auditor encuentra un gap entre lo que la sesión que ejecuta la
> fase aislada del plan dice que implementó en su handoff, y lo que el
> handoff auditor encuentra -hay que tener cuidado porque aquí hay cosas
> que se responden yendo a ctx 7 y hay otras que se responden primero
> verificado cómo funciona el flujo agentico y después yendo a ctx 7-.
> Cuando eso ocurre, actualmente se produce un gap. Md, y se acude a un
> prompt que proporciona plan.md para luego ir y pegar ese prompt en una
> sesión aislada que, a partir del prompt, la fase especificada en
> detallada en el (la parte del plan que le tocaba a esa sesion), el tag
> de deuda técnica asociado al gap y no se exactamente que otras cosas,
> “resuelve” el gap. Quiero validar con información fiable y actualizada
> recogida ante las máximas fuentes de autoridad en la materia (ctx7 +
> web para confirmar) qué es lo que dicha información sugiere frente a
> todo esto y qué es lo que dice que es lo correcto, óptimo y pertinente
> que podemos y/o deberíamos (o nó) hacer en nuestro caso particular y
> por qué.

\*\*\*NOTA: Me puse a analizar en qué casos podría suceder que un
criterio nunca pudiera ser confirmado y llegué a la conclusión de que
así como en el caso de las premisas sucede que una premisa no puede ser
confirmada si fue mal acotada (las recomendaciones de la fuente sobre
una premisa descartada, si no entran en el alcance son la confirmación
de que la premisa nació mal acotada), en el caso de los criterios sucede
que un criterio no puede ser confirmado si es excluyente frente al plan
mismo; las afirmaciones validables que constituyen los criterios que se
evalúan en la rúbrica deben ser un todo que refleja de forma correcta
cuál es el molde del que tiene que salir cada plan, De modo que un
criterio disonante o que no tenga sentido puede hacer que un plan bien
formulado nunca apruebe la rúbrica. por eso es muy importante que los
criterios tengan sentido. Deuda verificador revisa la deuda técnica y
redacta en la sección análisis del verificador qué es lo que el plan
debería resolver y qué no debería tocar. Plan redactor utiliza eso como
insumo, pero también contrasta el patrón de deuda técnica contra el
código fuente (de hecho, no lo hace actualmente; confía al 100% en en
análisis del verificador, pero se validará en otro inciso numerado de
este documento si tiene sentido que haga solo eso o si sí debería
re-confirmar), y concluido ese análisis, arma el borrador inicial del
plan. El inciso b del paso 6 hace que cada afirmación validable y
pertinente en el borrador inicial del plan (como trade-offs, decisiones
arquitectónicas, etc) se se convierta en premisas (las cuales deberían
estar bien acotadas, porque salen de un borrador de plan construido a
partir del alcance indicado en la sección análisis del verificador) y
asegura que dichas premisas sean correctas, ajustando el borrador del
plan (cuyo alcance debería estar bien acotado desde lectura del análisis
del verificador) hasta que quede no solamente bien acotado, sino con las
premisas correctas (algunas premisas no tendrán fuente aplicable, pero
aquellas del tipo “la mejor forma de hacer x en el contexto de un
backend con tales cosas es y” podrán ser validadas contra fuentes, para
que detalles técnicos de implementación sean los correctos, más óptimos
y pertinentes). El paso c, Se asegura que ese plan tenga la forma que
debería tener. Es decir, se construye un plan bien acotado del que se
extraen premisas. Ese plan resuelve el problema correcto. Y Luego b se
encarga que esas premisas constituyan un plan que no solo resuelve el
problema correcto, sino que además ese problema correcto es resuelto de
la forma óptima pertinente y adecuada en nuestro caso particular de
acuerdo a las fuentes aplicables, y c se encarga de que ese plan que
resuelve el problema correcto lo resuelva de la forma correcta de
acuerdo a nuestro caso particular.

Si va a existir un apartado en la sección “fuentes de autoridad” que
detalle las citas por decisión, hay que tomar en consideración los
diferentes tipos de fuentes de origen que existen para cada evidencia
involucrada en la toma de decisiones; si se habla de decisiones sobre si
un criterio es confirmado o contradicho, entonces tenemos como principal
fuente de origen de las evidencias (que se utilizan para confirmar o
contradecir una premisa) a las fuentes de “autoridad en la materia”, que
son todos aquellos recursos disponibles a través de internet a través de
la web (solo sitios web que cumplan con estos 3 checks: link accesible y
funcional, recurso verificado, y versión actualizada del recurso
verificado consultado en el caso) o a través del mcp de context 7. Pero
también existen otro tipo de fuentes; aquellas como ficheros.md o
ficheros.py, e incluso otras que el agente utilice bajo su propio
criterio cuando no haya fuentes de autoridad disponibles, las cuales
también proporcionan evidencia que se puede llegar a utilizar para
confirmar o contradecir una premisa dentro del inciso b del paso 6 del
procedimiento numerado en plan-redactor.md. Ahora, si hablamos sobre las
decisiones que se toman frente a los criterios de la rúbrica y si un
plan los cumple o nó en la sección c del paso 6 del procedimiento
numerado de plan-redactor.md, entonces también sucede que existen estos
mismos tipos de fuente de donde provienen las evidencias. Y si los links
que se detallan en cita por decisión solo existen para la toma de
algunas decisiones y no todas -asumiendo que allí no se cita haciendo
referencia a rutas a nivel de SO, sino solo con links cuando los hay-
(que además son decisiones sobre si el plan sufrió modificaciones o nó
en función de la confirmación o contradicción de sus premisas y
criterios) Entonces me cuestiono ¿cuál la verdadera utilidad de las
citas por decisión si ya existen las bitácoras? Puedo inferir que su
propósito inicial era el de servirme a mí para nutrir mi bibliografía
pero ahora me pregunto si en verdad vale la pena que ese apartado
exista, o si solamente va a dar citas que representan información “a
medias” sobre decisiones que involucraron el análisis a más fuentes que
no se citan, mientras al mismo tiempo existe el riesgo que el agente
empiece a alucinar o a agotar su ventana de contexto detallando
información para la bibliografía de mis informes al tiempo que debe
concentrarse en otro tipo de tareas no ligadas a la escritura académica.

| **Prioridad** | **Fase de Saneamiento**                                                                    | **Incisos de tu Documento**                                                    | **Justificación Técnica (según Fuentes de Autoridad)**                                                                                                                                                                                                                        |
|---------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Fase 1**    | **Frontera Cognitiva y Entrada de Datos (*Upstream Grounding*)**                           | **12, 18, 22** (junto con **15, 16, 16.1, 17**)                                | Resuelve primero el *Context Rot* (Anthropic) decidiendo qué delegar entre deuda-verificador y plan-redactor, y cierra la fuga de falsos negativos e indefinición ante deuda «desmentida» en el nodo 1 (LangGraph).                                                           |
| **Fase 2**    | **Cierre de Bucles de Control y Condiciones de Salida (*Control Flow & Exit Conditions*)** | **3.2, 3.2.1, 7, 7.1** (Rúbrica) y **13, 13.1, 16.2, 16.3, 19, 20** (Premisas) | Ataca los **faltantes estructurales del bucle Evaluador-Optimizador** (Anthropic/OpenAI): fija cómo se extraen premisas, cómo se decide sin fuente externa, el orden exacto de iteración de la rúbrica y la condición de salida cuando se agotan las 2 rondas de un criterio. |
| **Fase 3**    | **Invariantes de Estado, No-Regresión y *Scope Creep***                                    | **10, 10.1, 10.2, 21, 21.1, 21.1.1, 21.1.2** + **3, 3.1, 3.1.1, 5, 6**         | Una vez que los bucles b y c tienen flujo y salida claros, defines las reglas de mutación de estado para que ajustar el plan no invalide premisas/criterios previos ni introduzca *scope creep*, y afinas la redacción de C2, C4 y C5.                                        |
| **Fase 4**    | **Estandarización de Artefactos Documentales (*Structured Note-Taking & Logging*)**        | **4, 3.3, 14, 14.1, 1, 1.1, 1.1.1, 2, 8, 9, 11**                               | Con la lógica de iteración y el presupuesto de contexto ya definidos, creas el Delta y la Bitácora de la Rúbrica que faltaban, defines las columnas de evidencia multinivel y depuras «Citas por decisión» sin riesgo de sobrecargar al agente.                               |
| **Fase 5**    | **Verificación Post-Ejecución (*Handoff & Gaps*)**                                         | **23**                                                                         | Cierra el último eslabón de la cadena (handoff-auditor y gap.md), aplicando guardarraíles contra la complacencia de las sesiones ejecutoras.                                                                                                                                  |
