import json
import unittest
import webtest
import os

from api.src import movements

class MovementTest(unittest.TestCase):
  def testConsistentOpponents_ten_three(self):
    movement = movements.Movement(10, 3, 7)
    self.checkConsistentSchedule(movement, 10, 3)
    self.checkConsistentOpponents(movement, 10, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 10, 3)
    self.checkTableConsistency(movement, 10, 3)
    
  def testConsistentOpponents_ten_two(self):
    movement = movements.Movement(10, 2, 7)
    self.checkConsistentSchedule(movement, 10, 2)
    self.checkConsistentOpponents(movement, 10, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 10, 2)
    self.checkTableConsistency(movement, 10, 2)

  def testConsistentOpponents_nine_two_eight(self):
    movement = movements.Movement(9, 2, 8)
    self.checkConsistentSchedule(movement, 9, 2)
    self.checkConsistentOpponents(movement, 9, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 2)
    self.checkTableConsistency(movement, 9, 2)
    
  def testConsistentOpponents_nine_three_eight(self):
    movement = movements.Movement(9, 3, 8)
    self.checkConsistentSchedule(movement, 9, 3)
    self.checkConsistentOpponents(movement, 9, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 3)
    self.checkTableConsistency(movement, 9, 3)
    
  def testConsistentOpponents_nine_two_seven(self):
    movement = movements.Movement(9, 2, 7)
    self.checkConsistentSchedule(movement, 9, 2)
    self.checkConsistentOpponents(movement, 9, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 2)
    self.checkTableConsistency(movement, 9, 2)
    
  def testConsistentOpponents_nine_three_seven(self):
    movement = movements.Movement(9, 3, 7)
    self.checkConsistentSchedule(movement, 9, 3)
    self.checkConsistentOpponents(movement, 9, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 3)
    self.checkTableConsistency(movement, 9, 3)
 
  def testConsistentOpponents_eight_two_six(self):
    movement = movements.Movement(8, 2, 6)
    self.checkConsistentSchedule(movement, 8, 2)
    self.checkConsistentOpponents(movement, 8, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 8, 2)
    self.checkTableConsistency(movement, 8, 2)
    
  def testConsistentOpponents_eight_three_six(self):
    movement = movements.Movement(8, 3, 6)
    self.checkConsistentSchedule(movement, 8, 3)
    self.checkConsistentOpponents(movement, 8, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 8, 3)
    self.checkTableConsistency(movement, 8, 3)
  
  def testConsistentOpponents_seven_two_seven(self):
    movement = movements.Movement(7, 2, 7)
    self.checkConsistentSchedule(movement, 7, 2)
    self.checkConsistentOpponents(movement, 7, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 7, 2)
    self.checkTableConsistency(movement, 7, 2)
 
  def testConsistentOpponents_seven_three_seven(self):
    movement = movements.Movement(7, 3, 7)
    self.checkConsistentSchedule(movement, 7, 3)
    self.checkConsistentOpponents(movement, 7, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 7, 3)
    self.checkTableConsistency(movement, 7, 3)
  
  def checkConsistentSchedule(self, movement, num_pairs, num_hands_per_round):
    for i in range(num_pairs):
      opponents_played = set()
      hands_played = set()
      rounds_played = set()
      for round in movement.GetMovement(i + 1):
        self.assertIsNotNone(round)
        opp = round.get('opponent')
        self.assertIsNotNone(opp)
        self.assertFalse(opp in opponents_played,
                         msg="Opponent {} for pair {} is played more than once".format(
                             opp, i + 1))
        opponents_played.add(opp)

        round_no = round.get('round')
        self.assertIsNotNone(round_no)
        self.assertFalse(round_no in rounds_played,
                         msg="Round {} for pair {} is played more than " + 
                             "once".format(round_no, i + 1))
        rounds_played.add(round_no)

        hands = round.get('hands')
        self.assertIsNotNone(hands)
        self.assertEqual(num_hands_per_round, len(hands),
                         msg="Round {} for pair {} has {} hands. Expected {}".format(
                             round_no, i + 1, len(hands), num_hands_per_round))
        for hand in hands:
          self.assertFalse(hand in hands_played, 
                           msg=("Hand {} for pair {} is played more than " + 
                               "once").format(hand, i + 1))
          hands_played.add(hand)
        position = round.get('position')
        self.assertEqual(2, len(position))
        self.assertTrue(int(position[0]) <= num_pairs/2, 
                        msg="Invalid table specification {} for pair {}".format(
                            position, i + 1))
        self.assertTrue(position[1] in ("E", "N"), 
                        msg="Invalid position specification {} for pair {}".format(
                            position, i + 1))


  def checkConsistentOpponents(self, movement, num_pairs, num_hands_per_round):
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        round_no = round.get('round')
        hands = round.get('hands')
        opp = round.get('opponent')
        opp_movement = movement.GetMovement(opp)
        position = round.get('position')
        found_match = False
        for opp_round in opp_movement:
          if round_no != opp_round.get('round'):
            continue
          found_match = True
          self.assertEqual(hands, opp_round.get('hands'), 
                           msg=("Round {} hands for pair {} are inconsistent " + 
                               "with opponent pair {}'s hands").format(
                                   round_no, i+1, opp))
          self.assertEqual(i + 1, opp_round.get('opponent'),
                           msg=("Round {} opponent for pair {} is inconsistent " + 
                               "with pair {}").format(round_no, i + 1, opp))
          opp_position = opp_round.get('position')
          self.assertEqual(position[0], opp_position[0],
                           msg=("Pair {} and pair {} seem to be sitting at " + 
                               "different tables for round {}").format(
                                   i + 1, opp, round_no))
          self.assertNotEqual(position[1], opp_position[1],
                              msg=("Pair {} and pair {} seem to be sitting in " +
                                  "the same seat for round {}").format(
                                      i + 1, opp, round_no))
        self.assertTrue(found_match,
                        msg="Opponent {} of Pair {} doesn't seem to have them for round {}".format(
                            opp, i + 1, round_no))
  
  def checkHandsPlayedRightNumberOfTimes(self, movement, num_pairs,
                                         num_hands_per_round):
    non_relay_hands = {}
    relay_hands = {}
    total_times_played = {}
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        round_no = round.get('round')
        hands = round.get('hands')
        if round.get('relay_table'):
          for hand in hands:
            if not relay_hands.get(round_no):
              relay_hands[round_no] = {}
            relay_hands[round_no][hand] = relay_hands[round_no].get(hand, 0) + 1
            total_times_played[hand] = total_times_played.get(hand, 0) + 1
        else: 
          for hand in hands:
            if not non_relay_hands.get(round_no):
              non_relay_hands[round_no] = {}
            non_relay_hands[round_no][hand] = non_relay_hands[round_no].get(
                hand, 0) + 1
            total_times_played[hand] = total_times_played.get(hand, 0) + 1
    
    for r, hl in non_relay_hands.items():
      for h, n in hl.items():
        self.assertEqual(2, n,
                         msg=("Non relay hand {} is played {} times in round " + 
                             "{}").format(h, n, r))
        self.assertTrue((not relay_hands.get(r)) or (not relay_hands[r].get(h)), 
                        msg="Non relay hand {} is present in relay table".format(h))

    for r, hl in relay_hands.items():
      for h, n in hl.items():
        self.assertTrue(n > 2,
                        msg=("Relay hand {} is played only {} times in round " + 
                            "{}. Must be > 2.").format(h, n, r))
        self.assertTrue(n % 2 == 0,
                        msg=("Relay hand {} is played {} times in round {}. " + 
                            "Must be divisible by 2").format(h, n, r))
        self.assertTrue((not non_relay_hands.get(r)) or (not non_relay_hands[r].get(h)), 
                        msg="Relay hand {} is present in non-relay table".format(h))
    first_number_played = total_times_played[1]
    for h, n in total_times_played.items():
      self.assertEqual(first_number_played, n, 
                       msg=("Hand {} is played {} times, wheras hand 1 is " + 
                           "played {} times.").format(h, n, first_number_played))

  def checkTableConsistency(self, movement, num_pairs, num_hands_per_round):
    positions = {}
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        round_no = round.get('round')
        position = round.get('position')[0]
        if not positions.get(position):
          positions[position] = {round_no : [i + 1]}
        else:
          positions[position][round_no] = positions[position].get(round_no, []) + [i + 1]
          
    for t, rt in positions.items():
      for r, n in rt.items():
        self.assertEqual(2, len(n), 
                         msg=("Table {} hosts a weird number of teams ({}) in " + 
                             "round {}.").format(t, n, r))
  