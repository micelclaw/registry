# Modification notices — Office 0.2.0

Notice issued **17 November 2026** by **Micelclaw (Víctor García Valdunciel)**.
The application sources listed below modify Puter Technologies Inc. software
at HeyPuter/everything revision `2c593c5be59294690baf0a69b62fa64c1fd3628f`.
This dated supplement accompanies the historical source archives without
changing their bytes or replacing original copyright/licence notices. It does
not assert that every modified file already carries a sufficient notice.

## documents 0.2.0

Modified revision: `8d9f98fc8d16239d0970644c5facac589c781043`; recorded commit date: 2026-11-17T06:47:31+01:00.
Upstream path: `src/documents`. Source archive SHA-256: `df31af20dc9a2c0b7dde937f31e6232fa13138635fb35852eec737c3c6741142`.

Changes made by Micelclaw (preserving upstream attribution):

- editorView: almacenamiento Drive, autoguardado CAS e identidad Micelclaw; protección de compatibilidad
- File nativo: recientes de Drive, plantillas, importación, guardar copia y compartir con identidad confirmada
- Agente de Micelclaw y colaboración Yjs a través de Core, sin SDK/cuenta de Puter
- Estilos DOCX duplicados: precedencia primera definición ECMA-376-1 §17.7.4.17, normalización al exportar sin eliminar declaraciones
- Tema y locale conectados al shell; traducción común pendiente

The archive includes the modified vendor source and new `src/`, `tools/`
service/build integrations; the complete diff can be reconstructed against the
identified upstream revision. Puter engine and its bounded vendor changes remain MIT; new wrapper/tools
retain BUSL-1.1 as detailed in the package LICENSE.

## spreadsheets 0.2.0

Modified revision: `5a731d57aa9373d6c65ca8dd9a8b583187138b59`; recorded commit date: 2026-11-17T02:49:18+01:00.
Upstream path: `src/spreadsheet`. Source archive SHA-256: `469695e661cfb05458d404f20294e290e92f1c4466446ab941c7cf4356f23b40`.

Changes made by Micelclaw (preserving upstream attribution):

- Almacenamiento Drive con CAS, cola por archivo y comprobación de actor
- Plantillas/importaciones: sin compartir ni agente hasta guardar una identidad propia
- Menús AI conectados al panel del agente Micelclaw, sin API/cuenta Puter
- Historial SDK desactivado: un solo XLSX, Version history abre versiones Core en Drive

The archive includes the modified vendor source and new `src/`, `tools/`
service/build integrations; the complete diff can be reconstructed against the
identified upstream revision. Application changes are distributed under AGPL-3.0-only; separately licensed
dependencies/assets keep their original terms.

## presentations 0.2.0

Modified revision: `bf57d10a59d682e1189ae03bf40962ec127219f8`; recorded commit date: 2026-11-17T06:53:14+01:00.
Upstream path: `src/presentation`. Source archive SHA-256: `84a084ec5000949990732c6a2f88a918998f7d4b1dcb0ff8bde5f71ba3330cea`.

Changes made by Micelclaw (preserving upstream attribution):

- Almacenamiento Drive con CAS, cola por archivo y comprobación de actor
- Plantillas/importaciones: sin compartir ni agente hasta guardar una identidad propia
- Menús AI conectados al panel del agente Micelclaw, sin API/cuenta Puter
- Recientes nativos usan actividad Drive y despacho Office autorizado; primer guardado de plantillas automático

The archive includes the modified vendor source and new `src/`, `tools/`
service/build integrations; the complete diff can be reconstructed against the
identified upstream revision. Application changes are distributed under AGPL-3.0-only; separately licensed
dependencies/assets keep their original terms.

## pdf 0.2.0

Modified revision: `b2ef57053a0ee06c223a70f0e264baa501655f34`; recorded commit date: 2026-11-17T07:25:38+01:00.
Upstream path: `src/pdf`. Source archive SHA-256: `2bda28a72dd28a1f298ea038a80f4bd99c90257329bbb94037eaddc047a5e443`.

Changes made by Micelclaw (preserving upstream attribution):

- Almacenamiento Drive con CAS, cola por archivo e identidad Micelclaw
- Importación de PDF/imágenes: contexto propio sin identidad/solo lectura heredados del archivo anterior
- Primer guardado automático de la importación, compartir/agente sólo tras persistencia confirmada
- Menús de abrir/guardar apuntan a Drive, sin SDK/cuenta Puter

The archive includes the modified vendor source and new `src/`, `tools/`
service/build integrations; the complete diff can be reconstructed against the
identified upstream revision. Application changes are distributed under AGPL-3.0-only; separately licensed
dependencies/assets keep their original terms.

