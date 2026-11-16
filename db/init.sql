CREATE TABLE IF NOT EXISTS categorias (
  id_categoria INT AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_categoria)
);
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INT AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(150) NOT NULL,
  PRIMARY KEY (id_usuario),
  UNIQUE (correo)
);
CREATE TABLE IF NOT EXISTS libros (
  id_libro INT AUTO_INCREMENT,
  titulo VARCHAR(200) NOT NULL,
  autor VARCHAR(150) NOT NULL,
  isbn VARCHAR(20) NOT NULL,
  id_categoria INT NOT NULL,
  PRIMARY KEY (id_libro),
  FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);
CREATE TABLE IF NOT EXISTS reservas (
  id_reserva INT AUTO_INCREMENT,
  fecha_reserva DATE NOT NULL,
  id_usuario INT NOT NULL,
  id_libro INT NOT NULL,
  PRIMARY KEY (id_reserva),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
  FOREIGN KEY (id_libro) REFERENCES libros(id_libro)
);
