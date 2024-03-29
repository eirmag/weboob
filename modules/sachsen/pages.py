# -*- coding: utf-8 -*-

# Copyright(C) 2010-2012 Romain Bignon, Florent Fourcot
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime, date, time
from weboob.tools.browser import BasePage
from weboob.capabilities.gauge import Gauge, GaugeMeasure, GaugeSensor
from weboob.capabilities.base import NotAvailable, NotLoaded


__all__ = ['ListPage', 'HistoryPage']


class ListPage(BasePage):
    def get_rivers_list(self):
        for pegel in self.document.getroot().xpath(".//a[@onmouseout='pegelaus()']"):
            data = pegel.attrib['onmouseover'].strip('pegelein(').strip(')').replace(",'", ",").split("',")
            gauge = Gauge(int(data[7]))
            gauge.name = unicode(data[0].strip("'"))
            gauge.city = gauge.name.split(' ')[0]  # TODO: real regexp to remove the number
            gauge.object = unicode(data[1])

            sensors = []
            try:
                lastdate = date(*reversed([int(x) for x in data[2].split(' ')[0].split(".")]))
                lasttime = time(*[int(x) for x in data[2].split(' ')[1].split(":")])
                lastdate = datetime.combine(lastdate, lasttime)
            except:
                lastdate = NotAvailable

            bildforecast = data[5]
            if bildforecast == "pf_gerade.png":
                forecast = u"stable"
            elif bildforecast == "pf_unten.png":
                forecast = u"Go down"
            elif bildforecast == "pf_oben.png":
                forecast = u"Go up"
            else:
                forecast = NotAvailable

            try:
                level = float(data[3])
                levelsensor = GaugeSensor(gauge.id + "-level")
                levelsensor.name = u"Level"
                # TODO levelsensor.unit =
                levelsensor.forecast = forecast
                lastvalue = GaugeMeasure()
                lastvalue.level = level
                lastvalue.date = lastdate
                # TODO lastvalue.alarm =
                levelsensor.lastvalue = lastvalue
                levelsensor.history = NotLoaded
                levelsensor.gaugeid = gauge.id
                sensors.append(levelsensor)
            except:
                pass
            try:
                flow = float(data[4])
                flowsensor = GaugeSensor(gauge.id + "-flow")
                flowsensor.name = u"Flow"
                # TODO flowsensor.unit =
                flowsensor.forecast = forecast
                lastvalue = GaugeMeasure()
                lastvalue.level = flow
                lastvalue.date = lastdate
                # TODO lastvalue.alarm =
                flowsensor.lastvalue = lastvalue
                flowsensor.history = NotLoaded
                flowsensor.gaugeid = gauge.id
                sensors.append(flowsensor)
            except:
                pass

            gauge.sensors = sensors

            yield gauge


class HistoryPage(BasePage):
    def iter_history(self, sensor):
        table = self.document.getroot().cssselect('table[width="215"]')
        lines = table[0].cssselect("tr")
        lines.pop(0)  # remove header
        lines.pop(0)  # remove first value (already in lastvalue)
        for line in lines:
            history = GaugeMeasure()
            leveldate = date(*reversed([int(x) for x in line[0].text_content().split(' ')[0].split(".")]))
            leveltime = time(*[int(x) for x in line[0].text_content().split(' ')[1].split(":")])
            history.date = datetime.combine(leveldate, leveltime)

            if sensor.name == u"Level":
                try:
                    history.level = float(line[1].text_content())
                except:
                    history.level = NotAvailable
            elif sensor.name == u"Flow":
                try:
                    history.level = float(line[2].text_content())
                except:
                    history.level = NotAvailable

            # TODO: history.alarm
            yield history
