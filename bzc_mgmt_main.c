#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <errno.h>

#include "bzc_mgmt.h"

/* use this to call bluez "mgmt" API as described in bluez-src-folder/doc/mgmt-api.txt */

int mgmt_create(void)
{
	struct sockaddr_hci addr;
	int fd;

	fd = socket(PF_BLUETOOTH, SOCK_RAW | SOCK_CLOEXEC | SOCK_NONBLOCK,
                                                                BTPROTO_HCI);
	if (fd < 0)
		return -errno;

	memset(&addr, 0, sizeof(addr));
	addr.hci_family = AF_BLUETOOTH;
	addr.hci_dev = HCI_DEV_NONE;
	addr.hci_channel = HCI_CHANNEL_CONTROL;

	if (bind(fd, (struct sockaddr *) &addr, sizeof(addr)) < 0) {
		int err = -errno;
		close(fd);
		return err;
	}

	return fd;
}

int hex_str_to_bin(char* in, char* out)
{
	/*get hex string into byte array*/
	char* nptr = in;
	int slen = strlen(in);
	char* nptr_invalid = in + slen;

	int byte;				  
	int bin_len = 0;
	
	while(nptr<nptr_invalid)
	{
		if(*nptr==' ' || *nptr=='\n' || *nptr=='\r')
		{
			nptr++;
		}
		else
		{
			sscanf(nptr,"%x",&byte);
			out[bin_len] = byte;    
			bin_len++;
			//			  printf("%02x ",byte);

			nptr+=2;
		}
	}
	return bin_len;
}

void print_hex(const char* buf, int len)
{
  int i=0;
  for(;i<len;i++)
    {
      printf("%02X ", (uint8_t) buf[i]);
    }
}

int main(int argc, char **argv)
{
	enum {BIN_BUF_MAX_LEN=10240};
	uint8_t bin_buf[BIN_BUF_MAX_LEN];
	int bin_buf_len = 0;

	printf("bzc_mgmt: this is a caller for bluez-mgmt api\n");

	if (argc != 2 || (argc == 2 && strncmp(argv[1],"-h",2) == 0) ) {
		printf("usage: bzc_mgmt '<COMMAND HEX SEPARTED BY SPACE>'\n"
			"Example to 'Read frist controller info':\n"
			"bzc_mgmt '04 00 00 00 00 00'\n\n"
			" - if successful would produce something like:\n"
			"(see protocol description in bluez-src-folder/doc/mgmt-api.txt)\n\n"
			"read response: 01 00 00 00 1B 01 04 00 00 49 06 69 71 A4 E4 08 02 00 FF FF 00 00 DA 0A 00 00 00 00 00 6B 61 73 69 64 69 74 2D 74 68 69 6E 6B 70 61 64 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
			"\n\n"
			"which compose of:\n"
			"event_code: 01 00\n"
			"controller_index: 00 00\n"
			"param_len: 1B 01\n"
			"request command_code: 04 00\n"
			"request result: 00 (means success)\n"
			"bluetooth_device_address: 49 06 69 71 A4 E4 (this is little endian so address is: E4-A4-71-69-06-49)\n"
			"and other params...\n"
			
			
			);
		return -1;
	}

	printf("command_hex string: %s\n", argv[1]);

	bin_buf_len = hex_str_to_bin(argv[1], bin_buf);
	printf("command_hex converted len: %d\n", bin_buf_len);
	printf("command_hex converted contents: ");
	print_hex(bin_buf, bin_buf_len);
	printf("\n");

	if (bin_buf_len < sizeof(struct mgmt_pkt)) {
		printf("INVALID: parsed specified command_hex len is less than minimum sizeof(struct mgmt_pkt): %lu\n",sizeof(struct mgmt_pkt));
		return -2;	
	} 

	int fd = mgmt_create();	
	printf("mgmt_create ret %d\n", fd);
	
	if (fd < 0) {
		printf("bzc_mgmt: FATAL: failed to open bluez mgmt socket"
			"- make sure you have CAP_NET_ADMIN capability (or try run using root)"
			"- ABORT\n");
		return -3;
	}

	int wret = write(fd, bin_buf, bin_buf_len);
	printf("write bin_buf wret %d\n", wret);

	enum {READ_BUF_MAX_LEN = 100000};
	uint8_t* read_buf = NULL;
	read_buf = malloc(READ_BUF_MAX_LEN);
	if (read_buf == NULL) {
		printf("bzc_mgmt: FATAL: failed to malloc read_buf - ABORT\n");
		close(fd);
		return -4;
	}
	
	int rret;
	
	while(1) {
		rret = read(fd, read_buf, BIN_BUF_MAX_LEN);
		if (rret < 0) {
			printf("\nread response ended - break\n");
			break;
		}
		printf("read response: ");
		print_hex(read_buf, rret);
	}

	/* this main function (program) shall return the last 'Command Complete events' error code if found */
	int ret = -1;
	if (rret >= sizeof(struct mgmt_pkt) + sizeof(struct resp_header)) {
		uint8_t* ptr;

		ptr = read_buf;
		
		struct mgmt_pkt* pevent_pkt = (struct mgmt_pkt*) ptr;
		ptr += sizeof(struct mgmt_pkt);
		printf("last event_pkt code: 0x%04X\n", pevent_pkt->code);
		printf("last event_pkt controller_id: 0x%04X\n", pevent_pkt->controller_id);
		printf("last event_pkt parm_len: 0x%04X\n", pevent_pkt->param_len);

		struct resp_header* presp_header = (struct resp_header*) ptr;
		ptr += sizeof(struct resp_header);
		printf("last resp_hedaer req_code: 0x%04X\n", presp_header->req_code);
		printf("last resp_hedaer error_code: 0x%04X\n", presp_header->error_code);
		ret = (int) presp_header->error_code;
		printf("set parsed error_code as ret code %d\n", ret);
		
		
	} else {
		printf("WARNING: failed to get respose err code for last response - resp too short - min len is %lu\n", sizeof(struct mgmt_pkt) + sizeof(struct resp_header));
	}

	/*
	struct mgmt_pkt* pevent_resp = NULL;
	pcmd_req = (struct mgmt_pkt*) malloc(sizeof(struct mgmt_pkt));
	
	if (pcmd_req == NULL) {
		printf("bzc_mgmt: FATAL: failed to malloc pcmd_req - ABORT\n");
		return -2;
	}
	
	memset(pcmd_req, 0, sizeof(struct mgmt_pkt));
	*/
	

	close(fd);
	
	return ret;
}
