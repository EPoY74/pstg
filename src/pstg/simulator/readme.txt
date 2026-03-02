Запуск:                                                                                                                              
                                                                                                                                       
  .venv\Scripts\python.exe -m pstg.simulator.signals_server                                                                            
                                                                                                                                       
  По умолчанию он отдаёт:                                                                                                              
                                                                                                                                       
  - PT1 = 1.5                                                                                                                          
  - PT2 = 2.5                                                                                                                          
  - PT3 = 3.5                                                                                                                          
  - FlowPerHour = 120.25                                                                                                               
  - FlowAmount = 456.75                                                                                                                
                                                                                                                                       
  Порт по умолчанию 1505, можно переопределить:                                                                                        

  .venv\Scripts\python.exe -m pstg.simulator.signals_server --host 0.0.0.0 --port 1505 --device-id 1 