ALTER TABLE usuarios
    ADD COLUMN clave_hash VARCHAR(255) NULL AFTER numero_identificacion;

ALTER TABLE canjes
    ADD COLUMN id_producto INT UNSIGNED NULL AFTER id_usuario;

CREATE INDEX idx_canjes_producto
    ON canjes (id_producto);

CREATE INDEX idx_movimientos_analisis
    ON movimientos_puntos (id_analisis);

CREATE INDEX idx_analisis_usuario_estado
    ON analisis_ia (id_usuario, estado_analisis);
