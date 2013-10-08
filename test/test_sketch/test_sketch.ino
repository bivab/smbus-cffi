#include <Wire.h>

#define I2C_SLAVE_ADDRESS 0x04
#define BUFFER_SIZE 32

#define WRITE_QUICK 1
#define READ_BYTE 2   
#define WRITE_BYTE 3
#define READ_BYTE_DATA 4
#define WRITE_BYTE_DATA 5
#define READ_WORD_DATA 6
#define WRITE_WORD_DATA 7
#define PROCESS_CALL 8
#define READ_BLOCK_DATA 9
#define WRITE_BLOCK_DATA 10
#define BLOCK_PROCESS_CALL 11
#define READ_I2C_BLOCK_DATA 12
#define WRITE_I2C_BLOCK_DATA 13

#define GETDATA 254
#define RESET 255

int testcase;
int testdata;
unsigned char tmp;
unsigned char reg;
String data;
unsigned char i2c_buffer[BUFFER_SIZE];
char serial_buffer[BUFFER_SIZE];

void setup() {
  Serial.begin(9600);
  Wire.begin(I2C_SLAVE_ADDRESS);
  Wire.onReceive(i2c_receive_handler);
  Wire.onRequest(i2c_request_handler);
  testcase = -1;
  data = "";
  reg = 255;
}

void loop() {
  if(testcase < 0 && Serial.available() > 0) {
    testcase = Serial.read();
    switch(testcase) {
      case WRITE_QUICK:
        setup_test_write_quick();
        break;
      case READ_BYTE:
        setup_test_read_byte();
        break;
      case WRITE_BYTE:
        setup_test_WRITE_BYTE();
        break;
      case READ_BYTE_DATA:
        setup_test_READ_BYTE_DATA();
      break;
      case WRITE_BYTE_DATA:
        setup_test_WRITE_BYTE_DATA();
        break;
      case READ_WORD_DATA:
        setup_test_READ_WORD_DATA();
        break;
      case WRITE_WORD_DATA:
        setup_test_WRITE_WORD_DATA();
        break;
      case PROCESS_CALL:
        break;
      case READ_BLOCK_DATA:
        setup_test_READ_BLOCK_DATA();
        break;
      case WRITE_BLOCK_DATA:
        setup_test_WRITE_BLOCK_DATA();
        break;
      case READ_I2C_BLOCK_DATA:
        setup_test_READ_I2C_BLOCK_DATA();
        break;
      case WRITE_I2C_BLOCK_DATA:
        setup_test_WRITE_I2C_BLOCK_DATA();
        break;
      case BLOCK_PROCESS_CALL:
      case -1:
        Serial.println("Error!!!");
      case RESET:
      default:
        reset();
    }  
  } else if(Serial.available() > 0) {
    tmp = Serial.read();
    switch(tmp) {
      case GETDATA:
        Serial.println(data);
        break;
      case RESET:
        reset();
        break;
    } 
  }
  delay(100);
}

void reset() {
  if(testcase > 0) {
    testcase = -1;
    data = "";
    // clear buffers
    while(Serial.available() > 0) {
      Serial.read();
    }
    while(Wire.available() > 0) {
      Wire.read();
    }
  }
}

void i2c_receive_handler(int numbytes) {
  switch(testcase) {
    case WRITE_QUICK:
      handle_WRITE_QUICK(numbytes);
      break;
    case READ_BYTE_DATA:
      handle_receive_READ_BYTE_DATA(numbytes);
      break;
    case READ_WORD_DATA:
      handle_receive_READ_WORD_DATA(numbytes);
      break;
    case WRITE_BYTE:
    case WRITE_BYTE_DATA:
    case WRITE_WORD_DATA:
    case WRITE_BLOCK_DATA:
    case WRITE_I2C_BLOCK_DATA:
      handle_WRITE_xxx(numbytes);
      break;
    case PROCESS_CALL:
      handle_receive_PROCESS_CALL(numbytes);
      break;
    case READ_BLOCK_DATA:
      handle_receive_READ_BLOCK_DATA(numbytes);
      break;
    case READ_I2C_BLOCK_DATA:
      handle_recieve_READ_I2C_BLOCK_DATA(numbytes);
      break;
    case BLOCK_PROCESS_CALL:
    default:
      data = "WTF!!!";
  }
}

void i2c_request_handler() {
  switch(testcase) {
    case READ_BYTE:
      handle_READ_BYTE();
      break;
    case READ_BYTE_DATA:
      handle_READ_BYTE_DATA();
      break;
    case READ_WORD_DATA:
      handle_READ_WORD_DATA();
      break;
    case PROCESS_CALL:
      handle_PROCESS_CALL();
      break;
    case READ_BLOCK_DATA:
      handle_READ_BLOCK_DATA();
      break;
    case READ_I2C_BLOCK_DATA:
      handle_READ_I2C_BLOCK_DATA();
      break;
    case BLOCK_PROCESS_CALL:
    default:
      Wire.write(-1);
  }
}

/* test write_quick */
void setup_test_write_quick() {
}
void handle_WRITE_QUICK(int numbytes) {
  data = "";
  data += testcase;
  data += "#";
  data += numbytes;
}


/* test read byte */
void setup_test_read_byte() { 
  while(Serial.available() <= 0) {
    // wait for data
    delay(100);
  }
  testdata = Serial.read();  
}

void handle_READ_BYTE() {
  Wire.write(testdata);
  data = "";
  data += testcase;
}

/* test write byte */
void setup_test_WRITE_BYTE() {
}

void handle_WRITE_BYTE(int numbytes) {
  testdata = Wire.read();
  data = "";
  data += testcase;
  data += "#";
  data += numbytes;
  data += "#";
  data += testdata;
}

/* test read byte data */
void setup_test_READ_BYTE_DATA() {
}

void handle_receive_READ_BYTE_DATA(int numbytes) {
  reg = Wire.read();
}
void handle_READ_BYTE_DATA() {
  testdata = 234;
  Wire.write(testdata);
  data = "";
  data +=  testcase;
  data += "#";
  data += reg;
  data += "#";
  data += testdata;
}

/* test write byte data */
void setup_test_WRITE_BYTE_DATA() {}
void handle_WRITE_BYTE_DATA(int numbytes) {
    data = "";
    data += testcase;
    data += "#";
    data += numbytes;
    data += "#";
    data += Wire.read();
    data += "#";
    data += Wire.read();
}

/* test read word data */
void setup_test_READ_WORD_DATA() {
  while(Serial.available() <= 0) {
    // wait for data
    delay(100);
  }
  Serial.readBytes(serial_buffer, 2);
  testdata = serial_buffer[0] << 8 | serial_buffer[1];  
  i2c_buffer[0] = serial_buffer[0];
  i2c_buffer[1] = serial_buffer[1];
}

void handle_receive_READ_WORD_DATA(int numbytes) {
  reg = Wire.read();
}

void handle_READ_WORD_DATA() {
  Wire.write(i2c_buffer, 2);
  data = "";
  data += testcase;
  data += "#";
  data += reg;
  data += "#";
  data += serial_buffer[0];
  data += serial_buffer[1];
}

/* test write word data */
void setup_test_WRITE_WORD_DATA() {}
void handle_WRITE_xxx(int numbytes) {
  data = "";
  data +=  testcase;
  data += "#";
  data += numbytes;
  data += "#";
  data += Wire.read();
  if(numbytes > 1) {
    data += "#";
    for(int i = 1; i < numbytes; i++) {
      data += Wire.read();
      if(i < numbytes - 1) {
        data += "|";
      }
    }
  }
}

/* test process call */
// no setup
void handle_receive_PROCESS_CALL(int numbytes) {
    reg = Wire.read();
    for(int i = 0; i < BUFFER_SIZE && Wire.available(); i++) {
      i2c_buffer[i] = Wire.read();
    }
}

void handle_PROCESS_CALL() {
  data = "";
  data += testcase;
  data += "#";
  data += reg;
  data += "#";
  data += i2c_buffer[0];
  data += "#";
  data += i2c_buffer[1];

  i2c_buffer[1] = 0xca;
  i2c_buffer[0] = 0xfe;
  // two bytes return value
  Wire.write(i2c_buffer, 2);
}

/* test read block data */
void setup_test_READ_BLOCK_DATA() {
  // prepare buffer to send block
  for(int i = 0; i < BUFFER_SIZE; i++) {
    i2c_buffer[i] = i + 100;
  }
}

void handle_receive_READ_BLOCK_DATA(int numbytes) {
  reg = Wire.read();
  Serial.write(reg);
  Serial.write(numbytes);
}
void handle_READ_BLOCK_DATA() {
  Wire.write(i2c_buffer, BUFFER_SIZE);
  data = "";
  data += testcase;
  data += "#";
  data += reg;
}


/* test write block data */
void setup_test_WRITE_BLOCK_DATA() {}

/* test read i2c block data */
void setup_test_READ_I2C_BLOCK_DATA() {
  // prepare buffer to send block
  for(int i = 0; i < BUFFER_SIZE; i++) {
    i2c_buffer[i] = 100+i;
  }
}
void handle_recieve_READ_I2C_BLOCK_DATA(int numbytes) {
  reg = Wire.read();
  tmp = numbytes;

}
void handle_READ_I2C_BLOCK_DATA() {
  data = "";
  data += testcase;
  data += "#";
  data += reg;
  data += "#";
  data += tmp;
  Wire.write(i2c_buffer, BUFFER_SIZE);
}

/* test WRITE_I2C_BLOCK_DATA */
void setup_test_WRITE_I2C_BLOCK_DATA() {}
