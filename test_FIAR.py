#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 08:12:31 2021

@author: dpetrovykh
"""
import unittest
import FIAR


class TestFIAR(unittest.TestCase):
    
    def test_switch_player(self):
        test_game = FIAR.FIAR.from_csv('test_game_1', folder=FIAR.TEST_FOLDER)     
        test_game.switch_player()
        self.assertEqual(test_game.next_player, 'red', "unexpected 'next_player'")
        
    def test_edge_coords(self):
        test_game = FIAR.FIAR.from_csv('test_game_1', folder=FIAR.TEST_FOLDER) 
        left_coords = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0)]
        top_coords = [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),(0,11)]
        right_coords = [(0,11),(1,11),(2,11),(3,11),(4,11),(5,11),(6,11),(7,11),(8,11),(9,11)]
        bottom_coords = [(9,0),(9,1),(9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),(9,9),(9,10),(9,11)]
        
        left_coords_calc = test_game.edge_coords('left')
        right_coords_calc = test_game.edge_coords('right')
        top_coords_calc = test_game.edge_coords('top')
        bottom_coords_calc = test_game.edge_coords('bottom')
        self.assertListEqual(left_coords_calc, left_coords)
        self.assertListEqual(right_coords_calc, right_coords)
        self.assertListEqual(top_coords_calc, top_coords)
        self.assertListEqual(bottom_coords_calc, bottom_coords)
        
    def test_num_steps(self):
        test_game = FIAR.FIAR.from_csv('test_game_2', folder=FIAR.TEST_FOLDER)
        
        for correct_val, start, dir_ in [(9,(0,0),(1,1)),
                                         (3,(6,0),(1,1)),
                                         (5,(0,4),(1,-1)),
                                         (5,(4,8),(-1,-1))]:
            calc = test_game.num_steps(start, dir_)            
            self.assertEqual(calc, correct_val)

    def test_extreme_points(self):
        points = [(-5,4),(4,-5),(-1,0),(1,-2)]
        self.assertEquals(FIAR.FIAR.extreme_points(points),((-5,4),(4,-5)))
        points = [(0,6),(0,-4),(0,0),(0,3)]
        self.assertEquals(FIAR.FIAR.extreme_points(points),((0,-4),(0,6)))

    def test_fill_line(self):
        points = [(0,0),(1,1),(3,3)]
        filled_points = FIAR.FIAR.fill_line(points)
        print(f"Filled points: {filled_points}")
        self.assertTupleEqual(filled_points, ((0,0),(1,1),(2,2),(3,3)))
        points = [(0,2), (1,1),(3,-1)]
        self.assertTupleEqual(FIAR.FIAR.fill_line(points),((0,2), (1,1),(2,0),(3,-1)))

if __name__ == '__main__':
    # Run the tests and print verbose output to stderr.
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFIAR))
    unittest.TextTestRunner(verbosity=2).run(suite)