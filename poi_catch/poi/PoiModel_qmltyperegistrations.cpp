/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#include <D:/Documents/py_project/poi_catch/poi_catch/models/PoiModel.py>


#if !defined(QT_STATIC)
#define Q_QMLTYPE_EXPORT Q_DECL_EXPORT
#else
#define Q_QMLTYPE_EXPORT
#endif
Q_QMLTYPE_EXPORT void qml_register_types_poi()
{
    qmlRegisterTypesAndRevisions<PoiModel>("poi", 1);
    QMetaType::fromType<QObject *>().id();
    qmlRegisterModule("poi", 1, 0);
}

static const QQmlModuleRegistration poiRegistration("poi", qml_register_types_poi);
