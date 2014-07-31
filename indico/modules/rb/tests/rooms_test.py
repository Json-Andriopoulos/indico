# -*- coding: utf-8 -*-
##
##
## This file is part of Indico.
## Copyright (C) 2002 - 2013 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.


from pprint import pprint
import transaction

from indico.core.db import db
from indico.modules.rb.models.room_attributes import RoomAttribute
from indico.modules.rb.models.room_equipments import RoomEquipment
from indico.modules.rb.models.rooms import Room
from indico.tests.db.data import *
from indico.tests.db.environment import DBTest
from indico.tests.db.util import diff


class TestRoom(DBTest):
    """
    Testing the most important functions of the Room class from
    the room booking models.
    """

    def iterRooms(self):
        for r in ROOMS:
            room = Room.find_first(Room.name == r['name'])
            yield r, room
            db.session.add(room)
        transaction.commit()

    def test_is_auto_confirm(self):
        for r, room in self.iterRooms():
            needs_confirmation = 'reservations_need_confirmation' in r and r['reservations_need_confirmation']
            assert_not_equal(room.is_auto_confirm, needs_confirmation)

    def test_available_video_conference(self):
        pass

    def test_bookable_time_per_day(self):
        for r, room in self.iterRooms():
            if 'bookable_times' in r:
                time_per_day = 0
                for x in r['bookable_times']:
                    time_per_day += (datetime.combine(date.today(), x['end_time']) -
                                     datetime.combine(date.today(), x['start_time'])).total_seconds()

                assert_equal(time_per_day, room.bookable_time_per_day)

            else:
                assert_equal(3600*24, room.bookable_time_per_day)

    def test_booking_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.booking_url, None)
            else:
                assert_is_not(room.booking_url, None)

    def test_details_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.details_url, None)
            else:
                assert_is_not(room.details_url, None)

    def test_full_name(self):
        for r, room in self.iterRooms():
            if room.has_special_name:
                assert_in(r['name'], room.full_name)
            assert_in(room.generateName(), room.full_name)

    def test_has_booking_groups(self):
        for r, room in self.iterRooms():
            assert_equal(room.has_booking_groups,
                         'attributes' in r and
                         any(attr['name'] == 'allowed-booking-group' for attr in r['attributes']))

    def test_has_projector(self):
        for r, room in self.iterRooms():
            assert_equal('equipments' in r and 'Computer Projector' in r['equipments'], room.has_projector)

    def test_has_special_name(self):
        for r, room in self.iterRooms():
            assert_equal(room.has_special_name, 'name' in r and r['name'] is not None)

    def test_has_webcast_recording(self):
        for r, room in self.iterRooms():
            assert_equal('equipments' in r and 'Webcast/Recording' in r['equipments'], room.has_webcast_recording)

    def test_is_public(self):
        for r, room in self.iterRooms():
            assert_equal(room.is_public, room.is_reservable and (not room.has_booking_groups))

    def test_kind(self):
        for r, room in self.iterRooms():
            if room.is_public:
                if room.is_auto_confirm:
                    assert_equal(room.kind, 'basicRoom')
                else:
                    assert_equal(room.kind, 'moderatedRoom')
            else:
                assert_equal(room.kind, 'privateRoom')

    def test_location_name(self):
        for r, room in self.iterRooms():
            found_in_data = False
            for loc in LOCATIONS:
                if room.location_name == loc['name']:
                    location_rooms = []
                    for loc_room in loc['rooms']:
                        location_rooms.append(loc_room['name'])
                    assert_in(room.name, location_rooms)
                    found_in_data = True
            assert_true(found_in_data)

    def test_marker_description(self):
        for r, room in self.iterRooms():
            description = room.marker_description
            if room.capacity:
                assert_in(str(room.capacity), description)
            if room.is_public:
                assert_in('public', description)
            else:
                assert_in('private', description)
            if room.is_auto_confirm:
                assert_in('auto-confirmation', description)
            else:
                assert_in('needs confirmation', description)
            if room.needs_video_conference_setup:
                assert_in('video conference', description)

    def test_needs_video_conference_setup(self):
        for r, room in self.iterRooms():
            if 'equipments' in r:
                assert_equal('Video conference' in r['equipments'], room.needs_video_conference_setup)
            else:
                assert_false(room.needs_video_conference_setup)

    def test_large_photo_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.large_photo_url, None)
            else:
                assert_is_not(room.large_photo_url, None)

    def test_small_photo_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.small_photo_url, None)
            else:
                assert_is_not(room.small_photo_url, None)

    def test_has_photo(self):
        for r, room in self.iterRooms():
            if room.photo_id is None:
                assert_false(room.has_photo)
            else:
                assert_true(room.has_photo)

    def test_has_equipment(self):
        for r, room in self.iterRooms():
            if 'equipments' in r:
                for equip in r['equipments']:
                    assert_true(room.has_equipment(equip))
            assert_false(room.has_equipment('This equipment does not exist'))

    def test_find_available_video_conference(self):
        pass

    def testGetAttributeByName(self):
        for r, room in self.iterRooms():
            if 'attributes' in r:
                for attr in r['attributes']:
                    assert_is_not(room.getAttributeByName(attr['name']), None)
            assert_is(room.getAttributeByName('This attribute does not exist'), None)

    def test_has_attribute(self):
        for r, room in self.iterRooms():
            if 'attributes' in r:
                for attr in r['attributes']:
                    assert_true(room.has_attribute(attr['name']))
            assert_false(room.has_attribute('This attribute does not exist'))

    def testGetLocator(self):
        for r, room in self.iterRooms():
            l = room.getLocator()
            assert_equal(l['roomLocation'], room.location.name)
            assert_equal(l['roomID'], room.id)

    def test_generate_name(self):
        for r, room in self.iterRooms():
            if room.building:
                assert_in(r['building'], room.generateName())
            if room.floor:
                assert_in(r['floor'], room.generateName())
            if room.number:
                assert_in(r['number'], room.generateName())

    def testGetFullName(self):
        for r, room in self.iterRooms():
            assert_in(room.name, room.getFullName())
            assert_in(room.generateName(), room.getFullName())

    def testUpdateName(self):
        for r, room in self.iterRooms():
            if room.building and room.floor and room.number:
                room.name = ''
                room.updateName()
                assert_true(len(room.name) > 0)

    def getAccessKey(self):
        """
        Nothing to test.
        """
        pass

    def testGetRoomWithDefaults(self):
        """
        Nothing to test.
        """
        pass

    def test_find_all(self):
        all_rooms = Room.find_all()

        lista = []
        #we get the concatenation of location.name and full name because
        #these values are used for sorting in the find_all method.
        for r, room in self.iterRooms():
            lista.append(room.location.name + room.getFullName())

        lista = sorted(lista)
        assert_equal(len(all_rooms), len(lista))

        for i in range(len(all_rooms)):
            assert_equal(all_rooms[i].location.name + all_rooms[i].getFullName(), lista[i])

    def find_with_attribute(cls, attribute):
        pass

    def getRoomsWithData(*args, **kwargs):
        pass

    def testGetMaxCapacity(self):
        max_capacity = 0
        for r, room in self.iterRooms():
            if 'capacity' in r:
                max_capacity = r['capacity'] if r['capacity'] > max_capacity else max_capacity
        assert_equal(max_capacity, Room.getMaxCapacity())

    def filter_available(start_dt, end_dt, repetition, include_pre_bookings=True, include_pending_blockings=True):
        pass

    def getRoomsForRoomList(form, avatar):
        pass

    def getResponsible(self):
        pass

    def getResponsibleName(self):
        pass

    def has_live_reservations(self):
        for r, room in self.iterRooms():
            def is_live(resv):
                #Live reservations: Happening now or future reservations.
                return resv['start_date'] >= datetime.datetime.utcnow() or \
                    resv['end_date'] >= datetime.datetime.utcnow()
            c = len(filter(is_live, r.get('reservations', []))) > 0
            assert_equal(c, room.doesHaveLiveReservations())

    def isAvatarResponsibleForRooms(avatar):
        pass

    def testGetEquipmentNames(self):
        pass
        #Does not work

    def removeEquipment(self, equipment_name):
        pass

    def get_blocked_rooms(self, *dates, **kwargs):
        pass

    def test_get_attribute_value(self):
        for r, room in self.iterRooms():
            if 'attributes' in r:
                for attr in r['attributes']:
                    assert_is_not(room.get_attribute_value(attr['name']), None)

    def _can_be_booked(self, avatar, prebook=False, ignore_admin=False):
        pass

    def test_can_be_booked(self):
        pass

    def can_be_overriden(self, avatar):
        pass

    def can_be_prebooked(self, avatar, ignore_admin=False):
        pass

    def can_be_modified(self, accessWrapper):
        pass

    def can_be_deleted(self, accessWrapper):
        pass

    def test_is_owned_by(self):
        pass

    def getGroups(self, group_name):
        pass

    def getAllManagers(self):
        pass

    def check_advance_days(self, end_date, user=None, quiet=False):
        pass

    def check_bookable_times(self, start_time, end_time, user=None, quiet=False):
        pass

    def test_get_nonbookable_days(self):
        for r, room in self.iterRooms():
            total_non_bookable_days = 0
            if 'nonbookable_dates' in r:
                for nmd in r['nonbookable_dates']:
                    total_non_bookable_days += (nmd['end_date'] - nmd['start_date']).days + 1
            assert_equal(room.get_nonbookable_days(INITIAL_DATE, FINAL_DATE), total_non_bookable_days)

        #receiving error for more than one non-bookable periods.
        #needs to be discussed.
