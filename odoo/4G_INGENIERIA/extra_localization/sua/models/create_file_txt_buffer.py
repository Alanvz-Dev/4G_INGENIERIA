
from io import BytesIO


import io
# Write a string to a buffer
output = io.StringIO()

line1 = "PS5 Restock India \n"
line2 = "Xbox Series X Restock India \n"
line3 = "Nintendo Switch Restock India"
output.writelines([line1, line2, line3]).encode("iso-8859-1")
print(type(output))
# Retrieve the value written
print(output.getvalue())
# Discard buffer memory
output.close()



# buffered = BytesIO()
# with open(buffered, 'w') as f:


#     f.writelines([line1, line2, line3])

#     print(buffered)

