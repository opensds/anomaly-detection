# Copyright 2019 The OpenSDS Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from flask import Flask
from anomaly_detection.api.services import service
from anomaly_detection import log


class ServerManager:
    app = Flask(__name__)

    def __init__(self):
        self._init_logging()
        self._init_server()

    def _init_logging(self):
        log.setup(log.Config, "manila")

    def _init_server(self):
        self.app.url_map.strict_slashes = False
        # register router
        self.app.register_blueprint(service)

    def start(self):
        self.app.run("127.0.0.1", "8085")


def main():
    server_manager = ServerManager()
    server_manager.start()


if __name__ == '__main__':
    sys.exit(main())
