import java.io.*;
import java.net.*;

package DriveChino;

public class Servidor {
    public static void main(String[] args) {

       try { //Crep el try catch porque voy a trabajar con flujos de datos y sockets

            // Crear el socket del servidor 1234 para no olvidar xd
            ServerSocket serverSocket = new ServerSocket(1234);
            System.out.println("Servidor iniciado en el puerto 1234");
            
            // Asociar el servidor a una carpeta
            File folder = new File("/ruta/a/la/carpeta");
            if (!folder.exists()) {
                folder.mkdirs();
            }
            // Esperar a que un cliente se conecte
            System.out.println("Esperando conexiones...");
            Socket clientSocket = serverSocket.accept();
            System.out.println("Cliente conectado: " + clientSocket.getInetAddress().getHostAddress());
            
            // Obtener los flujos de entrada y salida del socket
            InputStream inputStream = clientSocket.getInputStream();
            OutputStream outputStream = clientSocket.getOutputStream();
            
            // Realizar las operaciones de lectura y escritura en el socket
            
            // Cerrar los flujos de entrada y salida
            inputStream.close();
            outputStream.close();
            
            // Cerrar el socket del cliente
            clientSocket.close();
            
            // Cerrar el socket del servidor
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}