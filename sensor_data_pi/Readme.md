1. Ladda hem projektet till din Raspberry pi
2. Om du vill att programmet startar av sig själv vid start av din Raspberry pi,
   följ dessa instruktioner annars följ instruktionerna i blocket under.
   1. Kontrollera att användare root på din pi har pipenv installerat.
   2. placera dig sedan under /etc/systemd/system och skapa som root en ny fil som heter *.service 
   3. i denna fil skall följande kod klistras in:
      [Unit]
      Description=Service for client.py
      Wants=network-online.target
      After=network.target network-online.target

      [Service]
      Restart=on-failure
      WorkingDirectory=/home/pi/python_project/Jordgubbarna/sensor_data_pi
      ExecStart=/home/pi/python_project/Jordgubbarna/sensor_data_pi/startup.sh

      [Install]
      WantedBy=multi-user.target
   4. se till att sökvägarna i filen stämmer för vart ditt projekt är placerat på din pi.
   5. kör: sudo systemctl daemon-reload
   6. kör: sudo systemctl enable *.service
   7. kör: sudo systemctl start *.service
   8. kontrollera att programmet är igång
   9. du är färdig.
4. Kontrollera att du har pipenv installerat, installera annars pipenv med hjälp av pip.
5. Ställ dig under sensor_data_pi och kör: pipenv install.
6. Nu bör du ha en virituell miljö där du kan köra ditt program.
7. starta programmet med pipenv run python client.py
8. Nu kan du starta din server på datorn.

I client.py ligger huvudprogrammet för klienten.
