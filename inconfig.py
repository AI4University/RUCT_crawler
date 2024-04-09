import configparser
configuracion = configparser.ConfigParser()

configuracion['principal']={'url':'https://www.educacion.gob.es/ruct/listaestudios?codigoEstado=&consulta=1&d-1335801-p=codigotablas&ambito=&codigoTipo=&descripcionEstudio=&codigoRama=&codigoEstudio=&situacion=&buscarHistorico=N&action:listaestudios=Consultar&actual=estudios&codigoSubTipo=&codigoUniversidad=universidad'}
configuracion['basico']={'url' : 'https://www.educacion.gob.es/ruct/solicitud/detalles?actual=menu.solicitud.basicos&cod=codigoin'}
configuracion['competencias'] ={'url':'https://www.educacion.gob.es/ruct/solicitud/competencias?actual=menu.solicitud.competencias.palabratipocomp&tipo=tipodecomp&cod=codigoin'}
configuracion['calendario'] ={'url':'https://www.educacion.gob.es/ruct/solicitud/calendarioImplantacion!cronograma?actual=menu.solicitud.calendarioImplantacion.cronograma&cod=codigoin'}
configuracion['modulo']={'url':'https://www.educacion.gob.es/ruct/solicitud/modulos?actual=menu.solicitud.planificacion.modulos&cod=codigoin'}
configuracion['metodologia']={'url':'https://www.educacion.gob.es/ruct/solicitud/metodologias?actual=menu.solicitud.planificacion.metodologias&cod=codigoin'}
configuracion['sistemaforma'] ={'url':'https://www.educacion.gob.es/ruct/solicitud/sistemas?actual=menu.solicitud.planificacion.sistemas&cod=codigoin'}
configuracion['pdf'] ={'url':'https://www.educacion.gob.es/ruct/solicitud/descripcionplan?actual=menu.solicitud.planificacion.descripcion&cod=codigoin'}

with open('inconfig.cfg','w') as archivoconfig:
    configuracion.write(archivoconfig)