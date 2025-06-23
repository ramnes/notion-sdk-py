import os
import asyncio
from typing import List


def split_file(file_path: str, chunk_size: int = 1024 * 1024 * 10) -> List[str]:
    """
    Split a file into chunks of a specified size.

    Args:
        file_path: Path to the input file (can be relative to the project).
        chunk_size: Size of each chunk in bytes.

    Returns:
        A list of file paths for the resulting chunks.
    """

    output_filenames = []

    # Get the file name
    file_name = os.path.basename(file_path)
    file_name_without_extention, _ = os.path.splitext(
        file_name
    )  # Remove file extension
    # create a directory for the split files
    file_split_name = file_name_without_extention + "_split"
    file_dir = os.path.join(os.path.dirname(file_path), file_split_name)
    os.makedirs(file_dir, exist_ok=True)  # create directory if it does not exist

    with open(file_path, "rb") as f:
        part_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # Generate chunk file names
            part_file_name = f"{file_name}.sf-part{part_num}"
            part_file_path = os.path.join(file_dir, part_file_name)

            # Write chunk files
            with open(part_file_path, "wb") as part_file:
                part_file.write(chunk)

            output_filenames.append(part_file_path)
            part_num += 1

    return output_filenames


async def split_file_async(
    file_path: str, chunk_size: int = 1024 * 1024 * 10
) -> List[str]:
    """
    Asynchronous version of the file splitting function.

    Args:
        file_path: Path to the input file (can be relative to the project).
        chunk_size: Size of each chunk in bytes.

    Returns:
        A list of file paths for the resulting chunks.
    """
    return await asyncio.get_event_loop().run_in_executor(
        None, split_file, file_path, chunk_size
    )


async def main():
    """
    Main function demonstrating the file splitting functionality.
    """

    file_path = r"examples\file_uploads\Glacier Warming.png"
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size / (1024 * 1024):.2f} MB")

    # Asynchronous call (corresponding to JavaScript's await)
    output_filenames = await split_file_async(file_path, 1024 * 1024 * 10)  # 10 MB

    print(type(output_filenames))

    print("Split files:")
    for split_file_path in output_filenames:
        print(split_file_path)

    return output_filenames


if __name__ == "__main__":
    # Run the asynchronous version
    asyncio.run(main())
