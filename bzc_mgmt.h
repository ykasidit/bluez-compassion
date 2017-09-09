#include <stdint.h>

/* see "mgmt" API as described in bluez-src-folder/doc/mgmt-api.txt */

/* both commands and events seem to have same structure */
struct __attribute__((__packed__)) mgmt_pkt {
	uint16_t code;
	uint16_t controller_id;
	uint16_t param_len;
};

struct __attribute__((__packed__)) resp_header {
	uint16_t req_code;
	uint8_t error_code;
};

enum {NON_CONTROLLER_ID=0xFFFF};
