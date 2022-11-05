from Map import *
from utilities import *
from GUI import GUI
class Application:    
    def simulate(self, map,  speed_limit, max_iter, frames_per_car, light_cycle_time, acceleration_exponent, left_prob, right_prob, visualise = False, debug = False): 
        Collisions = 0
        Flow = 0
        
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            map_img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
            map_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        start_time = time.time()
        
        i=0
        prev_flow = -1
        while(True):

            iter_start_time = time.time()
            i+=1
            if visualise:
                win.blit(map_img, map_rect)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()    
                    
                map.show_vehicles(win, debug)
            
            for road in map.roads:
                if visualise:
                    road.draw_traffic_light(win)

                for car in road.cars:
                    car.update_vision(road.direction, road.type, road.curve)
                    map.process_car_neighborhood(car, road)

            if i%frames_per_car == 0:
                map.spawn_car(speed_limit, acceleration_exponent)
            
            map.update_traffic_lights(i, light_cycle_time)
            Flow+=map.move_cars( right_prob, left_prob)
            Collisions+=map.check_for_car_collision()
            if visualise:
                pygame.display.update()
                clock.tick(FPS)

            elapsed_time = time.time() - start_time
            
            if i%600*FPS == 0:
                print(f"Flow: {Flow}, Collisions: {Collisions}, Time: {(elapsed_time)}, Cost: {cost_function(Flow, Collisions)}, FPS: {-1/(iter_start_time-time.time())}")
                if Flow == prev_flow:
                    break
                prev_flow = Flow
            #Endsd simulation if enough time has passed or if the crossroad got stuck
            if i >= max_iter:
                break
            
        return Flow, Collisions

        
if __name__ == '__main__':        
    app = Application()

    gui = GUI()
    gui.mainloop()
    data = gui.data
    acceleration_exponent = 4
    speed_limit = gui.data['Speed limit']
    frames_per_car = gui.data['Frames per car']
    max_iter = gui.data['Maximum iterations']
    left_prob = gui.data['Left turn prob']
    right_prob = gui.data['Right turn prob']
    light_cycle_time = gui.data['Traffic lights'][0][0]
    debug = gui.data['Debug']
    Flow, Collisions= app.simulate(generate_crossroad(WIDTH, HEIGHT), speed_limit, max_iter, frames_per_car, light_cycle_time, acceleration_exponent, left_prob, right_prob, visualise=True)
    print(Flow, Collisions)

    # speed_limit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car = run_gui()
